import hid

REPORT_TRUE = 255
REPORT_FALSE = 0


class HSFW:
    serial_number = '*********'
    firmware_version = 1.00
    _device = None
    _connected = False

    def getIsHomed(self):
        return self.get_hsfw_status()['is_homed']
    is_homed = property(getIsHomed)

    def getIsHoming(self):
        return self.get_hsfw_status()['is_homing']
    is_homing = property(getIsHoming)

    def getIsMoving(self):
        return self.get_hsfw_status()['is_moving']
    is_moving = property(getIsMoving)

    def getErrorState(self):
        return self.get_hsfw_status()['error_state']
    error_state = property(getErrorState)

    def get_wheel_id(self):
        return self.get_hsfw_description()['wheel_id']

    def get_serial_numbers():
        devs = hid.enumerate(0x10c4, 0x82cd)
        sns = []
        for dev in devs:
            sns.append(dev['serial_number'])
        return sns

    def _get_firmware_version(self):
        description = self.get_hsfw_description()

        major = int(description['firmware_major'])
        minor = int(description['firmware_minor']) / 10.0
        revision = int(description['firmware_revision']) / 100.0

        self.firmware_version = major + minor + revision
        return self.firmware_version


    def _get_serial_number(self):
        return self.serial_number

    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.open()

    def open(self, serial_number=None):
        if serial_number is not None:
            self.serial_number = serial_number

        if self._device is None:
            self._device = hid.device()
            self._device.open(0x10c4, 0x82cd, self.serial_number)

        _connected = True
        self._get_firmware_version()

    def close(self):
        if self._device is not None:
            self._device.close()
            self._device = None

        _connected = False

    def get_hsfw_status(self):
        res = self._device.get_input_report(10, 8)

        status = {
            "report_id": res[0],
            "is_homed": res[1] == REPORT_TRUE,
            "is_homing": res[2] == REPORT_TRUE,
            "is_moving": res[3] == REPORT_TRUE,
            "position": res[4],
            "error_state": res[5]
        }
        return status

    def get_hsfw_description(self):
        res = self._device.get_input_report(11, 8)

        status = {
            "report_id": res[0],
            "firmware_major": res[1],
            "firmware_minor": res[2],
            "firmware_revision": res[3],
            "filter_count": res[4],
            "wheel_id": chr(res[5]),
            "centering_offset": res[6],
        }
        return status

    def home(self):
        if self.error_state != 0:
            self.clear_error()

        report_id = 21
        report = [report_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if self._device.send_feature_report(report) == 0:
            raise Exception("Failed to home")

        res = self._device.get_feature_report(report_id, 14)
        if res == 0:
            raise Exception("Failed to home")

        if res[0] != report_id:
            raise Exception("Failed to home")

        home_resp = res[1]

        res = self._device.get_feature_report(report_id, 14)
        if res == 0:
            raise Exception("Failed to home")

        error_resp = res[1]

        if error_resp != REPORT_FALSE or home_resp != REPORT_TRUE:
            raise Exception("Failed to home")

    def move_to_filter(self, position):
        description = self.get_hsfw_description()

        if position < 1 or description['filter_count'] < position:
            raise Exception("{} is out of range. It must be between 1 and {}".format(
                position, description['filter_count']))

        report_id = 20
        report = [report_id, position, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if self._device.send_feature_report(report) == 0:
            raise Exception("Failed to move")

        res = self._device.get_feature_report(report_id, 14)
        if res == 0:
            raise Exception("Failed to move")

        if res[0] != report_id:
            raise Exception("Failed to move")

        move_resp = res[1]

        res = self._device.get_feature_report(report_id, 14)
        if res == 0:
            raise Exception("Failed to move")

        error_resp = res[1]

        if error_resp != REPORT_FALSE or move_resp != REPORT_TRUE:
            raise Exception("Failed to move")

    def number_of_filters(self):
        return self.get_hsfw_description()['filter_count']

    def get_current_filter(self):
        return self.get_hsfw_status()['position']

    def clear_error(self):
        self._device.write([2, 0])

    def get_wheel_name(self, wheel_id = None):
        if wheel_id is None:
            wheel_id = self.get_wheel_id()


        flash_read_wheel_name = 5
        name_report = [22, flash_read_wheel_name, ord(wheel_id), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
        if self._device.send_feature_report(name_report) == 0:
            raise Exception("Failed to get wheel name")
        
        resp1 = self._device.get_feature_report(22, 14)

        resp2 = self._device.get_feature_report(22, 14)

        if resp1[1] != resp2[1] or resp1[1] != flash_read_wheel_name:
            raise Exception("Failed to get wheel name")

        if resp1[2] != resp2[2] or resp1[2] != 0:
            raise Exception("Failed to get wheel name")

        if resp1[3] != resp2[3] or resp1[3] != ord(wheel_id):
            raise Exception("Failed to get wheel name")

        if resp1[4] != resp2[4] or resp1[4] != 0:
            raise Exception("Failed to get wheel name")

        return  bytes(resp2[6:]).decode('utf-8')

    def get_wheel_names(self):
        wheels = []

        for i in 'ABCDEFGHIJK':
            wheels.append(self.get_wheel_name(i))

        return wheels

    def get_filter_name(self, position = None, wheel_id = None):
        if wheel_id is None:
            wheel_id = self.get_wheel_id()

        if position is None:
            position = self.get_current_filter()

        flash_read_wheel_name = 3
        name_report = [22, flash_read_wheel_name, ord(wheel_id), position, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
        if self._device.send_feature_report(name_report) == 0:
            raise Exception("Failed to get filter name")
        
        resp1 = self._device.get_feature_report(22, 14)

        resp2 = self._device.get_feature_report(22, 14)

        if resp1[1] != resp2[1] or resp1[1] != flash_read_wheel_name:
            raise Exception("Failed to get filter name")

        if resp1[2] != resp2[2] or resp1[2] != 0:
            raise Exception("Failed to get filter name")

        if resp1[3] != resp2[3] or resp1[3] != ord(wheel_id):
            raise Exception("Failed to get filter name")

        if resp1[4] != resp2[4] or resp1[4] != position:
            raise Exception("Failed to get filter name")

        return  bytes(resp2[6:]).decode('utf-8')

    def get_filter_names(self, wheel_id=None):
        if wheel_id is None:
            wheel_id = self.get_wheel_id()

        filters = []

        for i in range(1, self.number_of_filters(wheel_id) + 1):
            filters.append(self.get_filter_name(i, wheel_id))

        return filters


    def number_of_filters(self, wheel_id = None):
        if wheel_id is None:
            wheel_id = self.get_wheel_id()

        if isinstance(wheel_id, str):
            wheel_id = bytes(wheel_id, 'utf-8')

        if wheel_id in b'ABCDE':
            return 5
        elif wheel_id in b'FGH':
            return 8
        elif wheel_id in b'IJK':
            return 7
        else:
            return self.get_hsfw_description()['filter_count']

    def set_filter_names(self, names, wheel_id = None):
        if wheel_id is None:
            wheel_id = self.get_wheel_id()

        if not self._check_valid_wheel_id(wheel_id):
            raise Exception("Invalid wheel_id")

        if len(names) is not self.number_of_filters(wheel_id):
            raise Exception("You must specify the correct number of names {} for this model.".format(
                self.number_of_filters(wheel_id)))

        for name in names:
            if name is None:
                raise Exception("Names must not be null")
            if len(name) > 8:
                raise Exception("Names must be less then 8 characters")
        index = 1
        for name in names:
            if name != self.get_filter_name(index):
                self.set_filter_name(name, index, wheel_id)
            index = index +1

    def set_filter_name(self, name, position, wheel_id = None):
        if wheel_id is None:
            wheel_id = self.get_wheel_id()

        if not self._check_valid_wheel_id(wheel_id):
            raise Exception("Invalid wheel_id")

        if self.firmware_version < 1.03 and wheel_id in 'IJK':
            raise Exception("Can't set IJK for older firmware")

        if name is None:
            raise Exception("Names must not be null")
        if len(name) > 8:
            raise Exception("Names must be less then 8 characters")

        flash_update_filter_name = 2
        flashops_command = 22

        name = name.ljust(8, ' ')

        data = [flashops_command, flash_update_filter_name, ord(wheel_id), position, ord(name[0]), ord(name[1]), ord(name[2]), ord(name[3]), ord(name[4]), ord(name[5]), ord(name[6]), ord(name[7]), 0, 0]

        if self._device.send_feature_report(data) == 0:
            raise Exception("Failed to set filter name")
        
        resp1 = self._device.get_feature_report(22, 14)

        resp2 = self._device.get_feature_report(22, 14)

        if resp1[1] != resp2[1] or resp1[1] != flash_update_filter_name:
            raise Exception("Failed to set filter name")

        if resp1[2] != resp2[2] or resp1[2] != 0:
            raise Exception("Failed to set filter name")

        if resp1[3] != resp2[3] or resp1[3] != ord(wheel_id):
            raise Exception("Failed to set filter name")

        if resp1[4] != resp2[4] or resp1[4] != position:
            raise Exception("Failed to set filter name")


    def _check_valid_wheel_id(self, wheel_id):
        return wheel_id in 'ABCDEFGHIJK'
