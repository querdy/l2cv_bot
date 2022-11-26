import mss
import numpy

def grab_image() -> numpy.array:
    mon = {"top": 0, "left": 0, "width": 1366, "height": 768}
    img = numpy.asarray(mss.mss().grab(mon))
    return img

def hide_parts_of_the_image(img: numpy.array) -> numpy.array:
    img[0:95, -95:-1] = 0  # радар
    img[-295:-1, 0:345] = 0  # чЯт
    img[-45:-1, 345:765] = 0  # скилы
    img[-115:-45, 345:700] = 0  # статус
    img[-155:-115, 345: 500] = 0  # таргет

    return img
