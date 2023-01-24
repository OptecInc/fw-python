import ifw 
import hsfw
import time
import copy

#This runs the Optec FilterWheel classes through their common methods.
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

    #Wait for the wheel to finish homing
    while wheel.is_homing:
        time.sleep(.01)

    if not wheel.is_homed:
        print("Failed to home wheel")
        return

    print(wheel.get_wheel_name('A'))

    for i in range(1, wheel.number_of_filters() + 1):
        wheel.move_to_filter(i)
        #Wait for the wheel to finish moving
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

def TestHSFW():
    for n in hsfw.HSFW.get_serial_numbers():
        print(n)

    #Use the first HSFW
    wheel = hsfw.HSFW(hsfw.HSFW.get_serial_numbers()[0])
    print(wheel.get_hsfw_status())
    print(wheel.get_hsfw_description())

    if wheel.error_state != 0:
        wheel.clear_error()

    print("testing HSFW")
    run_wheel_tests(wheel)  

def TestIFW(comport):
    print("testing IFW")
    wheel = ifw.IFW(comport)
    print(wheel.model)
    run_wheel_tests(wheel)  
  
#raise Exception("Select at least one test and then comment this out")

TestHSFW()
#Use the COM Port of your IFW / IFW2
TestIFW("COM3")