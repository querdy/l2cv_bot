import sys
import random
from enum import Enum
import threading
import time

import keyboard
from autohotpy.AutoHotPy import AutoHotPy
import cv2
import numpy
import mss
import argparse

from configure import config
from timer import TimerReset
from mixins import KeyboardAndMosueMixin, EntityGrabberMixin, StatusGrabberMixin
import dto

title = "admin"


class State(Enum):
    DO_NOTHING = 0
    DO_REGEN = 1
    REGEN = 2
    PICK_UP = 3
    ATTACK = 4
    FIND_MONSTER = 5
    CHOICE_TARGET = 6
    CHECK_TARGET = 7

class Core:
    def __init__(self):
        self.lock = threading.Lock()

        self.image = None
        self.image_2 = None

        self.start_screen_grabber()
        self.start_screen_updater()

        self.auto = AutoHotPy()
        self.start_auto()

    def run(self):
        raise NotImplementedError

    def start_screen_grabber(self) -> None:
        thread = threading.Thread(target=self.screen_grabber, name='grabber', daemon=True)
        thread.start()

    def screen_grabber(self) -> None:
        try:
            while True:
                with self.lock:
                    self.image = self.grab_image()
                time.sleep(0.01)
        except Exception as error:
            print(error)

    @staticmethod
    def grab_image() -> numpy.array:
        mon = {"top": config.top, "left": config.left, "width": config.width, "height": config.height}
        img = numpy.asarray(mss.mss().grab(mon))
        return img

    def start_screen_updater(self) -> None:
        thread = threading.Thread(target=self.screen_updater, name='screen_updater', daemon=True)
        thread.start()

    def screen_updater(self) -> None:
        while True:
            if self.image_2 is not None:
                cv2.imshow(title, self.image_2)

            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

            time.sleep(0.01)

    def get_screen(self) -> numpy.array:
        with self.lock:
            img = self.image.copy()
        return img

    def set_screen(self, img: numpy.array) -> None:
        with self.lock:
            self.image_2 = img.copy()

    def start_auto(self):
        self.auto.registerExit(self.auto.W, self.exitautohotpy)
        thread_auto = threading.Thread(target=self.auto.start, name='auto_hot_py', daemon=True)
        thread_auto.start()

    def exitautohotpy(self, *args):
        self.auto.stop()

class Bot(KeyboardAndMosueMixin, StatusGrabberMixin, EntityGrabberMixin, Core):

    def __init__(self):
        super().__init__()
        self.event = threading.Event()
        self.bad_target_timer = TimerReset(20, self._set_bad_target, daemon=True)

        # entity mixin
        self.entitys = dto.EntitysDTO()
        self.start_grab_entitys()

        # status mixin
        self.is_stand = True
        self.my_hp = None
        self.target_hp = None
        self.qty_turn = 1
        self.start_grab_stats()

        # other variables
        # bot states
        self.state = State.DO_NOTHING
        self.old_state = State.DO_NOTHING
        self.bad_target = False

        # skills
        self.attack = getattr(self.auto, f"N{config.attack}", self.auto.N1)
        self.pick_up = getattr(self.auto, f"N{config.pick_up}", self.auto.N4)
        self.next_target = getattr(self.auto, f"N{config.next_target}", self.auto.N9)
        self.sit = getattr(self.auto, f"N{config.sit}", self.auto.N0)

    def run(self) -> None:
        parser = argparse.ArgumentParser(description='Code for Image Segmentation with Distance Transform and Watershed Algorithm.\
            Sample code showing how to segment overlapping objects using Laplacian filtering, \
            in addition to Watershed and Distance Transformation')
        parser.add_argument('--input', help='Path to input image.', default='cards.png')
        args = parser.parse_args()
        while True:
            start_time = time.time()
            try:
                self.farm()
                if self.state != self.old_state:
                    print(self.state)
                self.old_state = self.state
            except Exception as error:
                print(error)
            time.sleep(0.01)
            # print("--- %s seconds ---" % (time.time() - start_time))

    def farm(self) -> None:
        image = self.get_screen()
        if self.state == State.DO_NOTHING:
            image = self._do_nothing(image)

        elif self.state == State.CHOICE_TARGET:
            image = self._choice_target(image)

        elif self.state == State.CHECK_TARGET:
            image = self._check_target(image)

        elif self.state == State.ATTACK:
            image = self._attack(image)

        elif self.state == State.PICK_UP:
            image = self._pick_up(image)

        elif self.state == State.DO_REGEN:
            image = self._do_regen(image)

        elif self.state == State.REGEN:
            image = self._regen(image)

        image = self.show_param(image)
        # image = cv2.GaussianBlur(image, (3, 3), 0)
        kernel = numpy.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=numpy.float32)
        imgLaplacian = cv2.filter2D(image, cv2.CV_32F, kernel)
        sharp = numpy.float32(image)
        imgResult = sharp - imgLaplacian
        imgResult = numpy.clip(imgResult, 0, 255)
        imgResult = imgResult.astype('uint8')
        imgLaplacian = numpy.clip(imgLaplacian, 0, 255)
        imgLaplacian = numpy.uint8(imgLaplacian)

        bw = cv2.cvtColor(imgResult, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(bw, 40, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        #
        dist = cv2.distanceTransform(bw, cv2.DIST_L2, 5)
        # cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)
        #
        # _, dist = cv2.threshold(dist, 0.4, 1.0, cv2.THRESH_BINARY)
        # kernel1 = numpy.ones((3, 3), dtype=numpy.uint8)
        # dist = cv2.dilate(dist, kernel1)
        #
        # dist_8u = dist.astype('uint8')
        #
        # contours, _ = cv2.findContours(dist_8u, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # markers = numpy.zeros(dist.shape, dtype=numpy.int32)
        # for i in range(len(contours)):
        #     cv2.drawContours(markers, contours, i, (i + 1), -1)
        #
        # cv2.circle(markers, (5, 5), 3, (255, 255, 255), -1)
        # markers_8u = (markers * 10).astype('uint8')
        # cv2.watershed(imgResult, markers)
        # mark = markers.astype('uint8')
        # mark = cv2.bitwise_not(mark)

        self.set_screen(imgLaplacian)

    def _do_nothing(self, image: numpy.array) -> numpy.array:
        self.bad_target = False
        self._check_is_stand()
        self.rotate(qty=self.qty_turn)
        self.event.clear()
        self.event.wait()
        # print(self.my_hp, self.is_stand)
        current_hp_percent = self.my_hp
        if current_hp_percent is not None and current_hp_percent < 70:
            self.state = State.DO_REGEN
            self.event.set()
            return image
        entitys = self.entitys
        if len(entitys.entitys) > 1:
            self.state = State.CHOICE_TARGET
        # else:
        #     self.event.clear()
        #     self.rotate()
        #     self.event.wait()
        if not self.is_stand:
            self.sit.press()
        return image

    def _choice_target(self, image: numpy.array) -> numpy.array:
        self._check_is_stand()
        entitys = self.entitys
        entitys = [entity for entity in entitys.entitys if entity.is_enemy]
        lens_before_monsters = {}
        # for entity in entitys:
        #     center = entity.center_point
        #     cv2.circle(image, (center[0], center[1]+30), 10, (255, 255, 255), 2)
        #     cv2.line(image, (config.width//2, config.height//2), (center[0], center[1] + 30), (255, 255, 255), 1)
        #     cv2.putText(image, str(entity.distace), (center[0], center[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
        #                 (255, 255, 255), 1, 1)
        #     if entity.distace > 700:
        #         continue
        #     with self.lock:
        #         self.image_2 = image
        #     lens_before_monsters.update({entity.distace: center})
        # if lens_before_monsters:
        #     lens_before_monsters = sorted(lens_before_monsters.items())
        #     for distance, point in lens_before_monsters:
        #         self.auto.LEFT_SHIFT.down()
        #         for y in range(10, 40, 10):
        #             self.auto.moveMouseToPosition(point[0], point[1]+y)
        #             self.left_click_target()
        #         time.sleep(.2)
        #         self.auto.LEFT_SHIFT.up()
        #         image_target = self.grab_image()
        #         target_hp_percent = self.target_hp
        #         if target_hp_percent is None:
        #             continue
        #         elif target_hp_percent > 0:
        #             break
        # self.state = State.CHECK_TARGET
        return image

    def _check_target(self, image: numpy.array) -> numpy.array:
        self._check_is_stand()
        self.target_hp_percent = self.target_hp
        if self.target_hp_percent == 100:
            if not self.bad_target_timer.is_alive():
                self.bad_target_timer.start()
                self.state = State.DO_NOTHING
            self.state = State.ATTACK
        if self.target_hp_percent is None or self.target_hp_percent < 100:
            self.state = State.DO_NOTHING
        return image

    def _attack(self, image: numpy.array) -> numpy.array:
        if self.bad_target:
            self.state = State.DO_NOTHING
            return image
        self._check_is_stand()
        self.attack.press()
        time.sleep(random.randint(30, 90) / 1000)
        target_hp = self.target_hp
        if target_hp == 0 or target_hp is None:
            self.attack.press()
            self.attack.press()
            time.sleep(random.randint(30, 90) / 1000)
            self.auto.ESC.press()
            time.sleep(random.randint(30, 90) / 1000)
            self.next_target.press()
            self.state = State.PICK_UP
        if not self.is_stand:
            self.state = State.DO_NOTHING
        return image

    def _pick_up(self, image: numpy.array) -> numpy.array:
        self._check_is_stand()
        for i in range(20):
            self.pick_up.press()
            time.sleep(random.randint(30, 90) / 1000)
        target_hp = self.target_hp
        if target_hp is not None:
            self.state = State.ATTACK
        else:
            self.qty_turn = self._find_min_distance_from_target()
            self.state = State.DO_NOTHING
        return image

    def _do_regen(self, image: numpy.array) -> numpy.array:
        self.sit.press()
        time.sleep(7)
        self.state = State.REGEN
        return image

    def _regen(self, image: numpy.array) -> numpy.array:
        if self.is_stand:
            self.next_target.press()
            self.state = State.ATTACK
            return image
        current_hp_percent = self.my_hp
        if current_hp_percent is not None and current_hp_percent > 95:
            self.sit.press()
            time.sleep(5)
            self.state = State.DO_NOTHING
        return image

    def show_param(self, image: numpy.array) -> numpy.array:
        cv2.putText(image, "self HP: " + str(self.my_hp) + "%", (770, 685), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, "target HP: " + str(self.target_hp) + "%", (770, 705), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, "state: " + ((str(self.state)).split('.')[1]), (770, 735), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, "is stand: " + str(self.is_stand), (770, 755), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        entitys = self.entitys
        entitys = [entity for entity in entitys.entitys if entity.is_enemy]
        for entity in entitys:
            center = entity.center_point
            cv2.circle(image, (center[0], center[1]+30), 10, (255, 255, 255), 2)
            cv2.line(image, (config.width//2, config.height//2), (center[0], center[1] + 30), (255, 255, 255), 1)
            cv2.putText(image, str(entity.distace), (center[0], center[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                        (255, 255, 255), 1, 1)
        return image

    def _check_is_stand(self):
        if not self.is_stand:
            self.sit.press()

    def _set_bad_target(self):
        print('kekw bad start')
        if self.target_hp == 100:
            self.auto.S.press()
            self.auto.ESC.press()
            self.bad_target = True

    def _find_min_distance_from_target(self):
        entity_mapper = []
        for i in range(9):
            self.rotate()
            self.event.clear()
            self.event.wait()
            with self.lock:
                entitys = self.entitys.entitys.copy()
            entitys_distances = [entity.distace for entity in entitys if entity.is_enemy]
            try:
                min_distance = min(entitys_distances)
            except ValueError:
                min_distance = 9999
            entity_mapper.append(min_distance)
        entity_mapper.remove(min(entity_mapper))
        min_distance = min(entity_mapper)
        return entity_mapper.index(min_distance) + 1


def wait_exit():
    keyboard.wait('q')
    sys.exit(0)


def main():
    bot = Bot()
    threading.Thread(target=wait_exit).start()
    threading.Thread(target=bot.run, daemon=True).start()


if __name__ == "__main__":
    main()
