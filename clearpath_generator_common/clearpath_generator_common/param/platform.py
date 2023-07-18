# Software License Agreement (BSD)
#
# @author    Roni Kreinin <rkreinin@clearpathrobotics.com>
# @copyright (c) 2023, Clearpath Robotics, Inc., All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of Clearpath Robotics nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Redistribution and use in source and binary forms, with or without
# modification, is not permitted without the express permission
# of Clearpath Robotics.

from clearpath_config.clearpath_config import ClearpathConfig
from clearpath_config.common.types.platform import Platform

from clearpath_generator_common.common import ParamFile, Package
from clearpath_generator_common.param.writer import ParamWriter


class PlatformParam():
    CONTROL = 'control'
    IMU_FILTER = 'imu_filter'
    LOCALIZATION = 'localization'
    TELEOP_INTERACTIVE_MARKERS = 'teleop_interactive_markers'
    TELEOP_JOY = 'teleop_joy'
    TWIST_MUX = 'twist_mux'

    class BaseParam():
        CLEARPATH_CONTROL = 'clearpath_control'
        CLEARPATH_PLATFORM = 'clearpath_platform'

        def __init__(self,
                     parameter: str,
                     clearpath_config: ClearpathConfig,
                     param_path: str) -> None:
            self.parameter = parameter
            self.clearpath_config = clearpath_config
            self.platform = self.clearpath_config.platform.get_model()
            self.namespace = self.clearpath_config.system.namespace
            print(self.namespace)
            self.param_path = param_path

            # Clearpath Platform Package
            self.clearpath_platform_package = Package(self.CLEARPATH_PLATFORM)
            self.clearpath_control_package = Package(self.CLEARPATH_CONTROL)

            # Default parameter file
            self.default_parameter_file_path = f'config/{self.platform}'
            self.default_parameter_file_package = self.clearpath_control_package
            self.default_parameter = self.parameter

            # Parameter file to generate
            self.param_file = ParamFile(
                name=self.parameter,
                namespace=self.namespace,
                path=self.param_path)

        def generate_parameters(self) -> None:
            # Default parameter file
            self.default_param_file = ParamFile(
                name=self.default_parameter,
                package=self.default_parameter_file_package,
                path=self.default_parameter_file_path,
                parameters={}
            )
            self.default_param_file.read()

            # TODO: Get user params
            self.param_file.parameters = self.default_param_file.parameters
            #print(self.param_file.parameters)

        def generate_parameter_file(self):
            param_writer = ParamWriter(self.param_file)
            param_writer.write_file()
            print(f'Generated config: {self.param_file.full_path}')

    class ImuFilterParam(BaseParam):
        def __init__(self,
                     parameter: str,
                     clearpath_config: ClearpathConfig,
                     param_path: str) -> None:
            super().__init__(parameter, clearpath_config, param_path)
            self.default_parameter_file_package = self.clearpath_platform_package
            self.default_parameter_file_path = 'config'

    class LocalizationParam(BaseParam):
        imu_config = [False, False, False,
                      False, False, False,
                      False, False, False,
                      False, False, True,
                      True, False, False]

        def generate_parameters(self) -> None:
            # Default parameter file
            self.default_param_file = ParamFile(
                name=self.default_parameter,
                package=self.default_parameter_file_package,
                path=self.default_parameter_file_path,
                parameters={}
            )
            self.default_param_file.read()

            self.param_file.parameters = self.default_param_file.parameters

            # TODO: Get user params
            if False:
                self.param_file.update(self.clearpath_config.platform.extras)
            else:
                if self.platform == Platform.J100:
                    imu0_parameters = {
                        'imu0': 'sensors/imu_0/data',
                        'imu0_config': self.imu_config,
                        'imu0_differential': False,
                        'imu0_queue_size': 10,
                        # Gravitational acceleration is removed in IMU driver
                        'imu0_remove_gravitational_acceleration': True
                    }
                    self.param_file.update({'ekf_node': imu0_parameters})

                # Add all additional IMU's
                imus = self.clearpath_config.sensors.get_all_imu()
                for imu in imus:
                    if imu.launch_enabled:
                        imu_name = imu.name.replace('_', '')
                        imu_parameters = {
                            imu_name: f'sensors/{imu.name}/data',
                            f'{imu_name}_config': self.imu_config,
                            f'{imu_name}_differential': False,
                            f'{imu_name}_queue_size': 10,
                            f'{imu_name}_remove_gravitational_acceleration': True
                        }
                        self.param_file.update({'ekf_node': imu_parameters})

    class TeleopJoyParam(BaseParam):
        def __init__(self,
                     parameter: str,
                     clearpath_config: ClearpathConfig,
                     param_path: str) -> None:
            super().__init__(parameter, clearpath_config, param_path)
            self.default_parameter_file_path = f'config/{self.platform}'
            self.default_parameter = f'teleop_{self.clearpath_config.platform.controller}'

    class TwistMuxParam(BaseParam):
        def __init__(self,
                     parameter: str,
                     clearpath_config: ClearpathConfig,
                     param_path: str) -> None:
            super().__init__(parameter, clearpath_config, param_path)
            self.default_parameter_file_path = 'config'

    PARAMETER = {
        CONTROL: BaseParam,
        IMU_FILTER: ImuFilterParam,
        LOCALIZATION: LocalizationParam,
        TELEOP_INTERACTIVE_MARKERS: BaseParam,
        TELEOP_JOY: TeleopJoyParam,
        TWIST_MUX: TwistMuxParam,
    }

    def __new__(cls,
                parameter: str,
                clearpath_config: ClearpathConfig,
                param_path: str) -> BaseParam:
        return PlatformParam.PARAMETER[parameter](parameter, clearpath_config, param_path)
