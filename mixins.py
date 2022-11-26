import functools
import time
import random
import numpy
import threading

import cv2
from autohotpy.InterceptionWrapper import InterceptionMouseState, InterceptionMouseStroke
import pytesseract
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from configure import config
import image_handling
from image_handling import monsters
import dto

class KeyboardAndMosueMixin:
    def left_click_target(self):
        stroke = InterceptionMouseStroke()
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
        self.auto.sendToDefaultMouse(stroke)
        time.sleep(random.randint(30, 110) / 1000)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
        self.auto.sendToDefaultMouse(stroke)
        time.sleep(random.randint(30, 110) / 1000)

    def rotate(self, qty: int = 1) -> None:
        self.auto.moveMouseToPosition(300, 500)
        stroke = InterceptionMouseStroke()
        time.sleep(random.randint(30, 80) / 1000)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
        self.auto.sendToDefaultMouse(stroke)
        time.sleep(random.randint(30, 80) / 1000)
        self.auto.moveMouseToPosition(300 + (9 * qty), 500)
        time.sleep(random.randint(30, 80) / 1000)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
        self.auto.sendToDefaultMouse(stroke)


class EntityGrabberMixin:
    def start_grab_entitys(self) -> None:
        thread = threading.Thread(target=self.grab_entitys, name='grab_entitys', daemon=True)
        thread.start()

    def grab_entitys(self) -> None:
        while True:
            image = self.get_screen()
            if image is not None:
                image_2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                image_2 = self.hide_parts_of_the_image(image_2)
                _, image_2 = cv2.threshold(image_2, 252, 252, cv2.THRESH_BINARY)
                # with self.lock:
                #     self.image_2 = image_2
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
                image_2 = cv2.morphologyEx(image_2, cv2.MORPH_CLOSE, kernel)
                image_2 = cv2.dilate(image_2, kernel, iterations=1)
                contours, _ = cv2.findContours(image_2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                # with self.lock:
                #     self.image_2 = image_2
                entitys = self._entity_classification(image, contours)
                myself = [entity for entity in entitys.entitys if entity.is_self]
                len_line = 100
                for my in myself:
                    center = my.center_point
                    len_line = numpy.sqrt(numpy.square(config.width//2 - center[0]) + numpy.square(config.height//2 - center[1]))
                with self.lock:
                    self.entitys = entitys
                    self.is_stand = len_line > 50
                    # self.image_2 = image_2
                    self.event.set()
            time.sleep(0.01)

    def _entity_classification(self, image: numpy.array, contours: numpy.array):
        entitys = dto.EntitysDTO()
        for contour in contours:
            start = time.time()
            counter = numpy.array([point[0] for point in contour])
            x, y, w, h = cv2.boundingRect(contour)
            image_2 = cv2.cvtColor(image[y: y + h, x:x + w], cv2.COLOR_BGR2GRAY)
            _, image_2 = cv2.threshold(image_2, 252, 252, cv2.THRESH_BINARY)
            start = time.time()
            # cv2.imshow('current', image_2)
            # if cv2.waitKey(25) & 0xFF == ord("q"):
            #     cv2.destroyAllWindows()
            img = tuple([tuple(row) for row in image_2])
            pcm6 = self._get_text_from_img(img)
            # time.sleep(4)
            # print(get_text_from_img.cache_info())
            if not pcm6.strip():
                continue
            entity = self._compare_names(pcm6=pcm6, mobs=monsters)
            # print(compare_names.cache_info())
            if entity is not None:
                center_point = image_handling.get_center_contour(contour)
                entity.contour = contour
                entity.center_point = center_point
                entity.entity_name = pcm6.lower()
                entity.distace = int(numpy.sqrt(numpy.square(config.width//2 - center_point[0]) + numpy.square(config.height//2 - center_point[1]+30)))
                entitys.entitys.append(entity)
            #     if entity.is_enemy:
            #         cv2.rectangle(image, (x + w, y + h), (x, y), (255, 255, 255), 1)
            #     else:
            #         cv2.rectangle(image, (x + w, y + h), (x, y), (0, 0, 0), 1)
            # with self.lock:
            #     self.image_2 = image
        # print("--- %s seconds ---" % (time.time() - start))
        return entitys

    @staticmethod
    def hide_parts_of_the_image(img: numpy.array) -> numpy.array:
        img[0:95, -95:-1] = 0  # радар
        img[-295:-1, 0:345] = 0  # чЯт
        img[-45:-1, 345:765] = 0  # скилы
        img[-115:-45, 345:700] = 0  # статус
        img[-155:-115, 345: 500] = 0  # таргет
        return img

    @staticmethod
    @functools.lru_cache(maxsize=256, typed=False)
    def _get_text_from_img(image: tuple):
        image = numpy.array(image)
        pcm6 = pytesseract.image_to_string(image, lang='eng', config=' --psm 6')
        return pcm6

    @staticmethod
    @functools.lru_cache(maxsize=256, typed=False)
    def _compare_names(pcm6: str, mobs: tuple) -> dto.EntityDTO | None:
        entity = dto.EntityDTO()
        # print(pcm6, '-->', process.extractOne(pcm6, monsters))
        if process.extractOne(pcm6, mobs)[1] > 85:
            # print(pcm6, '-->', process.extractOne(pcm6, monsters))
            entity.entity_name = pcm6.lower()
            entity.is_enemy = True
        elif fuzz.ratio(pcm6.lower(), config.player_name) > 90:
            entity.entity_name = pcm6.lower()
            entity.is_self = True
        if entity.entity_name is not None:
            return entity
        return None


class StatusGrabberMixin:
    def start_grab_stats(self) -> None:
        thread = threading.Thread(target=self.grab_stats, name='grab_stats', daemon=True)
        thread.start()

    def grab_stats(self) -> None:
        while True:
            image = self.get_screen()
            with self.lock:
                self.my_hp = image_handling.get_self_hp_percent(image)
                self.target_hp = image_handling.get_target_hp_percent(image)
            # print(self.my_hp, self.target_hp)
            time.sleep(0.01)