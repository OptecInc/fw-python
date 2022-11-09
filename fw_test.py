import ifw 
import hsfw
import time
import copy


def run_wheel_tests(wheel):
    print(wheel.serial_number)
    print(wheel.firmware_version)
    print(wheel.get_wheel_id())
    print(wheel.get_wheel_name())
    print(wheel.get_current_filter())
    print(wheel.get_filter_name())
    print(wheel.number_of_filters())

    for i in 'ABCDEFGHIJK':
            print("Number of filters for wheel {}: {}".format(i,wheel.number_of_filters(i)))

    wheel.home()

    while wheel.is_homing:
        time.sleep(.01)

    print(wheel.get_wheel_name('A'))

    for i in range(1, wheel.number_of_filters() + 1):
        wheel.move_to_filter(i)
        while wheel.is_moving:
            time.sleep(.01)
        print(wheel.get_current_filter())
        print(wheel.get_filter_name(wheel.get_current_filter()))

    print(wheel.get_filter_names())
    print(wheel.get_wheel_names())

    names = copy.deepcopy(wheel.get_filter_names())

    new_names = []

    for i in range(1, wheel.number_of_filters() + 1):
        new_names.append('QWER{}{}'.format(i, wheel.get_wheel_id()))

    wheel.set_filter_names(new_names)

    print(wheel.get_filter_names())
    print(new_names)

    wheel.set_filter_names(names)

    wheel.close()


for n in hsfw.HSFW.get_serial_numbers():
    print(n)

wheel = hsfw.HSFW(hsfw.HSFW.get_serial_numbers()[0])
print(wheel.get_hsfw_status())
print(wheel.get_hsfw_description())

if wheel.error_state != 0:
    wheel.clear_error()

print("testing HSFW")
run_wheel_tests(wheel)    

print("testing IFW")
ifw = ifw.IFW('COM3')
print(ifw.model)
run_wheel_tests(ifw)  
