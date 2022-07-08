# #!/usr/bin/env python3
# Importing time for time management
import time
import warnings

"""
Clamping function to check if the value is inbetween the limits
"""
def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value

try:
    # Get monotonic time to ensure that time deltas are always positive
    _current_time = time.monotonic
except AttributeError:
    # time.monotonic() not available (using python < 3.3), fallback to time.time()
    _current_time = time.time
    warnings.warn('time.monotonic() not available in python < 3.3, using time.time() as fallback')

class PID(object):
    """A PID Controller class 

    Methods
    -------
    compute(target, actual)
        Calculates the new output based on 
        the traditional PID formula
    
    integral_limits(limits)
        Limits the integral windup to the limits

    output_limits(limits)
        Limits the output to the limits

    output_offset(offset)
        Adds a offset to the computed output

    changeParameters(kp, ki, kd)
        Updates the controller terms
    """

    def __init__(self, kp=1.0, ki=0.0, kd=0.0, updateTime=0.01, direction=1, output_limits=(None, None), integral_limits=(None, None), output_offset=0.0):
        """
        Initialize a new PID controller.

        :param Kp: [float]: The value for the proportional gain Kp
        :param Ki: [float]: The value for the integral gain Ki
        :param Kd: [float]: The value for the derivative gain Kd
        :param direction: [int]: -1 for reverse, 1 for forward
        :param updateTime: [float]: The time in *seconds* which the controller should wait before generating
            a new output value. The PID works best when it is constantly called (eg. during a
            loop), but with a sample time set so that the time difference between each update is
            (close to) constant. If set to None, the PID will compute a new output value every time
            it is called.
        :param output_limits: [Tuple (lower, upper)] The initial output limits to use, given as an iterable with 2 elements, for example: (lower, upper).
            The output will never go below the lower limit or above the upper limit. Either of the limits can also be set to None to have no limit
            in that direction. Setting output limits also avoids integral windup, since the
            integral term will never be allowed to grow outside of the limits.
        :param integral_limits: [Tuple (lower, upper)] The initial intergral limits to use, given as an iterable with 2
            elements, for example: (lower, upper). The intergral will never go below the lower limit
            or above the upper limit. Either of the limits can also be set to None to have no limit
            in that direction. Setting output limits also avoids integral windup, since the
            integral term will never be allowed to grow outside of the limits.
        :param output_offset: [float]: Offset to be added at the output.
        """
        self.direction = direction
        self.changeParameters(kp, ki, kd)

        self.updateTime = updateTime
        self.lastUpdate = _current_time()

        self.output_limits = output_limits
        self.integral_limits = integral_limits

        self.output_offset = output_offset

        self.reset()

    def compute(self, target, actual):
        """
        Calulates the output based on the PID algorithm.

        :param target: [float]: Desired value.
        :param actual: [float]: Current value.

        :return output: [float]: The output correction.1
        """
        # first get the current time, and get the time difference with the last calculation
        now = _current_time()
        timeDifference = now - self.lastUpdate

        # only when the time has come calculate the new output, otherwise return the last output
        if timeDifference >= self.updateTime:
            # calc of current error
            current_error = target - actual

            # compute the proportional term
            self.pOutput = self.kp * current_error
            
            # compute the intergral term
            self.iOutput += self.ki * self.sum_error

            # Compute the derivative term
            self.dOutput += self.kd * self.last_error

            # clamp the intergral output    
            self.iOutput = _clamp(self.iOutput, self.integral_limits)
            
            # Compute final output
            self.output = self.output_offset + self.pOutput + self.iOutput + self.dOutput
            self.output = _clamp(self.output, self.output_limits)

            # Keep track of state
            self.lastActual = actual
            self.last_error = current_error
            self.sum_error += current_error
            self.lastUpdate = now
            
            return self.output
        else:
            return self.output

    @property
    def integral_limits(self):
        """
        Get the lower and upper limits for the intergral output.

        See also the *integral_limits* parameter in :meth:`PID.__init__`.
        """
        return self.lowerIntegralLimit, self.upperIntegralLimit

    @integral_limits.setter
    def integral_limits(self, limits):
        """
        Set the intergral limits. 

        Checks for valid input.
        """
        if limits is None:
            self.lowerIntegralLimit, self.upperIntegralLimit = None, None
            return

        lowerLimit, upperLimit = limits

        if (None not in limits) and (upperLimit < lowerLimit):
            raise ValueError('lower limit must be less than upper limit')

        self.lowerIntegralLimit = lowerLimit
        self.upperIntegralLimit = upperLimit

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper).

        See also the *output_limits* parameter in :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """
        Set the output limits. 

        Checks for valid input.
        """
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if (None not in limits) and (max_output < min_output):
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output

    @property
    def output_offset(self):
        """
        Adds a offset to the output directly, see :meth:`PID.__call__`.
        
        :param offset: [float]: Offset to be added to output.
        """
        return self.outputOffset

    @output_offset.setter
    def output_offset(self, offset):
        """
        Adds a offset to the output directly, see :meth:`PID.__call__`.
        
        :param offset: [float]: Offset to be added to output.
        """
        self.outputOffset = offset

    def changeParameters(self, kp, ki, kd):
        """
        Update the controller terms based on the *direction* set in :meth:`PID.__init__`.

        :param Kp: [float]: The value for the proportional gain Kp
        :param Ki: [float]: The value for the integral gain Ki
        :param Kd: [float]: The value for the derivative gain Kd
        """
        if self.direction < 0:
            self.kp = kp * -1
            self.ki = ki * -1
            self.kd = kd * -1
        else:
            self.kp = kp
            self.ki = ki
            self.kd = kd

    def reset(self):
        """
        Reset the PID controller internals.

        This sets each term to 0.0 as well as clearing the integral, the last output and the last
        input (derivative calculation).
        """
        self.output = 0.0
        self.pOutput = 0.0
        self.iOutput = 0.0
        self.dOutput = 0.0
        
        self.lastActual = 0.0

        self.last_error = 0.0
        self.sum_error = 0.0

        self.output = _clamp(self.output, self.output_limits)
        self.iOutput = _clamp(self.iOutput, self.integral_limits)

        self.lastUpdate = _current_time()
       

# Example of usage
if __name__ == "__main__":
    pid = PID(kp=2.0, ki=0.0, kd=0.0, integral_limits=(0, 10))
    pid.updateTime = 100
    pid.setOutputLimits(0, 100)

    while(True):
        output = pid.compute(50, 23)
        print(output)
