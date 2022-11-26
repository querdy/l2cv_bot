import json
import cv2
import numpy

monsters = []
with open('monsters.json', 'r') as f:
    mon = json.load(f)
    for m in mon:
        monsters.append(m)
monsters = tuple(monsters)

def get_center_contour(contour: numpy.array) -> list:
    moments = cv2.moments(contour)
    x = int(moments['m10'] / moments['m00'])
    y = int(moments['m01'] / moments['m00'])
    return [x, y]

def get_y_len_figure(image: numpy.array) -> int:
    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    counter = numpy.array([point[2][0] for point in contours])
    point_max = counter.max(axis=0, initial=None)
    point_min = counter.min(axis=0, initial=None)
    len_line = int((point_min[0] + point_max[0]) / 2)
    return len_line


def get_self_hp_percent(colored_image: numpy.array) -> int:
    max_hp = _get_self_max_hp(colored_image)
    current_hp = _get_self_current_hp(colored_image)
    try:
        current_hp_percent = int(current_hp / max_hp * 100)
        return current_hp_percent
    except:
        return None

def _get_self_max_hp(colored_image: numpy.array) -> int:
    hsv = cv2.cvtColor(colored_image[-95:-50, 350:700].copy(), cv2.COLOR_BGR2HSV)
    red_min = numpy.array([140, 100, 0])
    red_max = numpy.array([179, 255, 255])
    hsv = cv2.inRange(hsv, red_min, red_max)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    hsv = cv2.morphologyEx(hsv, cv2.MORPH_CLOSE, kernel)
    # hsv = cv2.erode(hsv, kernel, iterations=1)
    # hsv = cv2.dilate(hsv, kernel, iterations=1)
    contours_hp, _ = cv2.findContours(hsv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_hp:
        counter = numpy.array([point[0] for point in contour])
        point_max = counter.max(axis=0, initial=None)
        point_min = counter.min(axis=0, initial=None)
        hsv = cv2.rectangle(hsv, point_max, point_min, 255, -1)
    # cv2.imshow('max hp', hsv)
    # if cv2.waitKey(25) & 0xFF == ord("q"):
    #     cv2.destroyAllWindows()
    try:
        len_line = get_y_len_figure(hsv)
        # print('max', len_line)
        return len_line
        # return numpy.count_nonzero(hsv)
    except:
        return None

def _get_self_current_hp(colored_image: numpy.array) -> int:
    hsv = cv2.cvtColor(colored_image[-95:-50, 350:700].copy(), cv2.COLOR_BGR2HSV)
    red_min = numpy.array([160, 185, 120])
    red_max = numpy.array([179, 255, 200])
    hsv = cv2.inRange(hsv, red_min, red_max)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    hsv = cv2.morphologyEx(hsv, cv2.MORPH_CLOSE, kernel)
    # hsv = cv2.erode(hsv, kernel, iterations=1)
    # hsv = cv2.dilate(hsv, kernel, iterations=1)
    contours_hp, _ = cv2.findContours(hsv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_hp:
        counter = numpy.array([point[0] for point in contour])
        point_max = counter.max(axis=0, initial=None)
        point_min = counter.min(axis=0, initial=None)
        hsv = cv2.rectangle(hsv, point_max, point_min, 255, -1)
        # print(numpy.count_nonzero(hsv))
    # cv2.imshow('current', hsv)
    # if cv2.waitKey(25) & 0xFF == ord("q"):
    #     cv2.destroyAllWindows()
    try:
        len_line = get_y_len_figure(hsv)
        # print('curr', len_line)
        return len_line
        # return numpy.count_nonzero(hsv)
    except:
        return None

def get_target_hp_percent(colored_image: numpy.array) -> int:
    hsv = cv2.cvtColor(colored_image[-150:-110, 350:500], cv2.COLOR_BGR2HSV)
    max_hp = _get_target_max_hp(hsv)
    current_hp = _get_target_current_hp(hsv)
    try:
        current_hp_percent = int(current_hp / max_hp * 100)
        return current_hp_percent
        # print(f"self ХП: {int(self_current_hp / self_max_hp * 100)}%")
    except:
        return None

def _get_target_max_hp(hsv_image: numpy.array) -> int:
    hsv = hsv_image.copy()
    red_min = numpy.array([150, 50, 50])
    red_max = numpy.array([180, 255, 255])
    hsv = cv2.inRange(hsv, red_min, red_max)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    hsv = cv2.erode(hsv, kernel, iterations=1)
    hsv = cv2.dilate(hsv, kernel, iterations=1)
    contours_hp, _ = cv2.findContours(hsv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_hp:
        counter = numpy.array([point[0] for point in contour])
        point_max = counter.max(axis=0, initial=None)
        point_min = counter.min(axis=0, initial=None)
        hsv = cv2.rectangle(hsv, point_max, point_min, 255, -1)
    # cv2.imshow('max', hsv)
    # if cv2.waitKey(25) & 0xFF == ord("q"):
    #     cv2.destroyAllWindows()
    try:
        len_line = get_y_len_figure(hsv)
        # print(numpy.count_nonzero(hsv))
        return len_line
        # return numpy.count_nonzero(hsv)
    except:
        return None

def _get_target_current_hp(hsv_image: numpy.array) -> int:
    hsv = hsv_image.copy()
    red_min = numpy.array([160, 50, 50])
    red_max = numpy.array([175, 255, 255])
    hsv = cv2.inRange(hsv, red_min, red_max)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    hsv = cv2.erode(hsv, kernel, iterations=1)
    hsv = cv2.dilate(hsv, kernel, iterations=1)
    contours_hp, _ = cv2.findContours(hsv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_hp:
        counter = numpy.array([point[0] for point in contour])
        point_max = counter.max(axis=0, initial=None)
        point_min = counter.min(axis=0, initial=None)
        hsv = cv2.rectangle(hsv, point_max, point_min, 255, -1)
    # cv2.imshow('current', hsv)
    # if cv2.waitKey(25) & 0xFF == ord("q"):
    #     cv2.destroyAllWindows()
    try:
        len_line = get_y_len_figure(hsv)
        # print(numpy.count_nonzero(hsv))
        return len_line
        # return numpy.count_nonzero(hsv)
    except:
        return None
