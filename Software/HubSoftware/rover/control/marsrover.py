import math

rad2deg = 180.0 / math.pi

def opposite_angle(angle):
  if angle > 0:
    return angle - 180
  else:
    return angle + 180

def maprange(value, fromstart, fromend, tostart, toend, clip=False):
  if clip:
    if value < fromstart: return tostart
    if value > fromend: return toend
  mappedvalue = tostart + (toend - tostart) * float(value - fromstart) / float(fromend - fromstart)
  #print(f"Mapping {value} within {fromstart}...{fromend} to {mappedvalue} within {tostart}...{toend}")
  return mappedvalue

class Rover:

  def __init__(self, wf=53.3, wm=56.5, wr=56.5, lf=28.3, lr=26.3, sr=180):
    # Forward vector = [x=1,y=0]
    self._servorange = sr
    self._servocentre = sr / 2
    self._servooverlap = self._servocentre - 90
    self._flipfl = False
    self._flipfr = False
    self._flipml = False
    self._flipmr = False
    self._fliprl = False
    self._fliprr = False
    self._widthfront = wf
    self._widthmid = wm
    self._widthrear = wr
    self._lengthfront = lf
    self._lengthrear = lr
    # Radius (distance) of wheel from centre
    self._radfl = math.sqrt((0.25 * wf * wf) + lf * lf)
    self._radfr = self._radfl
    self._radml = 0.5 * wm
    self._radmr = self._radml
    self._radrl = math.sqrt((0.25 * wr * wr) + lr * lr)
    self._radrr = self._radrl
    self._maxrad = max([self._radrl, self._radml, self._radrl])
    # Angle of wheel plus 90 degrees to give turning angle
    # Python ATAN2(y,x) not (x,y)
    self._angfl = math.atan2(0.5 * wf, lf) - 0.5 * math.pi
    self._angfr = math.atan2(0.5 * -wf, lf) - 0.5 * math.pi
    self._angml = math.atan2(0.5 * wm, 0) - 0.5 * math.pi
    self._angmr = math.atan2(0.5 * -wm, 0) - 0.5 * math.pi
    self._angrl = math.atan2(0.5 * wr, -lr) - 0.5 * math.pi
    self._angrr = math.atan2(0.5 * -wr, -lr) - 0.5 * math.pi
    # Driving velocities
    self._drivefl = 0
    self._drivefr = 0
    self._driveml = 0
    self._drivemr = 0
    self._driverl = 0
    self._driverr = 0
    # Steering angles
    self._steerfl = 0
    self._steerfr = 0
    self._steerml = 0
    self._steermr = 0
    self._steerrl = 0
    self._steerrr = 0

  def flip_servo(self, angle, oldflip, debug=False):
    # Input angle forward = 0, turn left = +ve
    # Output angle forward = mid servo range, left = lower value because servo is upside-down
    # Swap order of destination range in map function calls if servo goes the wrong way
    # Move input into -180 to 180 range
    while angle > 180: angle -= 360
    while angle < -180: angle += 360
    limit = 90 + self._servooverlap # 90+45 for a 270deg servo, 90+0 for a 180deg servo
    if not oldflip: # Already in normal operation
      # Standard operation
      if -limit < angle < limit:
        # For 180deg servo, map input -90..90 to servo 180..0
        # For 270deg servo, map input -135..135 to servo 270..0
        ma = maprange(angle, -limit, limit, self._servorange, 0)
        if debug: print(f"Mapped {angle} to {ma} standard")
        return ma, False
      else:
        # Need to steer beyond servo limit so map to reverse direction and swap travel direction
        # For 180deg servo, maps -180..-90 to opposite 0..90 to servo 90..0 and input 90..180 to opposite -90..0 to servo 180..90
        # For 270deg servo, maps -180..-45 to opposite 0..135 to servo 135..0 and input 45..180 to opposite -135..0 to servo 270..135
        ma = maprange(opposite_angle(angle), -limit, limit, self._servorange, 0)
        if debug: print(f"Mapped {angle} to {ma} flipped")
        return ma, True
    else:
      # Already flipped
      oa = opposite_angle(angle)
      if -limit < oa < limit:
        ma = maprange(oa, -limit, limit, self._servorange, 0)
        if debug: print(f"Mapped opposite {oa} to {ma} still flipped")
        return ma, True
      else:
        ma = maprange(angle, -limit, limit, self._servorange, 0)
        if debug: print(f"Mapped {angle} to {ma} unflipped")
        return ma, False

  def set_control(self, dx=0, dy=0, dr=0, debug=False):
    scalevel = dr / self._maxrad
    # Angular velocity components
    avelfl = scalevel * self._radfl
    avelfr = scalevel * self._radfr
    avelml = scalevel * self._radml
    avelmr = scalevel * self._radmr
    avelrl = scalevel * self._radrl
    avelrr = scalevel * self._radrr
    # Combination of spin and drive
    velxfl = avelfl * math.cos(self._angfl) + dx
    velyfl = avelfl * math.sin(self._angfl) + dy
    velxfr = avelfr * math.cos(self._angfr) + dx
    velyfr = avelfr * math.sin(self._angfr) + dy
    velxml = avelml * math.cos(self._angml) + dx
    velyml = avelml * math.sin(self._angml) + dy
    velxmr = avelmr * math.cos(self._angmr) + dx
    velymr = avelmr * math.sin(self._angmr) + dy
    velxrl = avelrl * math.cos(self._angrl) + dx
    velyrl = avelrl * math.sin(self._angrl) + dy
    velxrr = avelrr * math.cos(self._angrr) + dx
    velyrr = avelrr * math.sin(self._angrr) + dy
    # Total velocity of each wheel
    velfl = math.sqrt(velxfl * velxfl + velyfl * velyfl)
    velfr = math.sqrt(velxfr * velxfr + velyfr * velyfr)
    velml = math.sqrt(velxml * velxml + velyml * velyml)
    velmr = math.sqrt(velxmr * velxmr + velymr * velymr)
    velrl = math.sqrt(velxrl * velxrl + velyrl * velyrl)
    velrr = math.sqrt(velxrr * velxrr + velyrr * velyrr)
    steerfl = math.atan2(velyfl, velxfl)
    steerfr = math.atan2(velyfr, velxfr)
    steerml = math.atan2(velyml, velxml)
    steermr = math.atan2(velymr, velxmr)
    steerrl = math.atan2(velyrl, velxrl)
    steerrr = math.atan2(velyrr, velxrr)
    if debug:
      print(f"FL:{velfl:.2f} @ {(steerfl * rad2deg):.2f} FR:{velfr:.2f} @ {(steerfr * rad2deg):.2f}")
      print(f"ML:{velml:.2f} @ {(steerml * rad2deg):.2f} MR:{velmr:.2f} @ {(steermr * rad2deg):.2f}")
      print(f"RL:{velrl:.2f} @ {(steerrl * rad2deg):.2f} RR:{velrr:.2f} @ {(steerrr * rad2deg):.2f}")
    maxvel = max([velfl, velfr, velml, velmr, velrl, velrr, 1.0]) 
    # Scale velocities back to max=1
    self._drivefl = velfl / maxvel
    self._drivefr = velfr / maxvel
    self._driveml = velml / maxvel
    self._drivemr = velmr / maxvel
    self._driverl = velrl / maxvel
    self._driverr = velrr / maxvel
    # Only steer if the wheel is moving
    if velxfl != 0 or velyfl !=0:
      # Steering directions
      self._steerfl, self._flipfl = self.flip_servo(steerfl * rad2deg, self._flipfl, debug)
      # Reverse direction for flipped wheels
      if self._flipfl: self._drivefl *= -1
    else:
      self._drivefl = 0
    if velxfr != 0 or velyfr !=0:
      self._steerfr, self._flipfr = self.flip_servo(steerfr * rad2deg, self._flipfr, debug)
      if self._flipfr: self._drivefr *= -1
    else:
      self._drivefr = 0
    if velxml != 0 or velyml !=0:
      self._steerml, self._flipml = self.flip_servo(steerml * rad2deg, self._flipml, debug)
      if self._flipml: self._driveml *= -1
    else:
      self._driveml = 0
    if velxmr != 0 or velymr !=0:
      self._steermr, self._flipmr = self.flip_servo(steermr * rad2deg, self._flipmr, debug)
      if self._flipmr: self._drivemr *= -1
    else:
      self._drivemr = 0
    if velxrl != 0 or velyrl !=0:
      self._steerrl, self._fliprl = self.flip_servo(steerrl * rad2deg, self._fliprl, debug)
      if self._fliprl: self._driverl *= -1
    else:
      self._driverl = 0
    if velxrr != 0 or velyrr !=0:
      self._steerrr, self._fliprr = self.flip_servo(steerrr * rad2deg, self._fliprr, debug)
      if self._fliprr: self._driverr *= -1
    else:
      self._driverr = 0

  def get_speeds(self):
    return [self._drivefl, self._drivefr, self._driveml, self._drivemr, self._driverl, self.driverr]

  def get_steers(self):
    return [self._steerfl, self._steerfr, self._steerml, self._steermr, self._steerrl, self._steerrr]

  def get_drive_front(self):
    return self._drivefl, self._steerfl, self._drivefr, self._steerfr

  def get_drive_mid(self):
    return self._driveml, self._steerml, self._drivemr, self._steermr

  def get_drive_rear(self):
    return self._driverl, self._steerrl, self._driverr, self._steerrr

  def get_wheel_pos_front(self):
    return self._radfl, (self._angfl+0.5*math.pi)*rad2deg, self._radfr, (self._angfr+0.5*math.pi)*rad2deg

  def get_wheel_pos_mid(self):
    return self._radml, (self._angml+0.5*math.pi)*rad2deg, self._radmr, (self._angmr+0.5*math.pi)*rad2deg

  def get_wheel_pos_rear(self):
    return self._radrl, (self._angrl+0.5*math.pi)*rad2deg, self._radrr, (self._angrr+0.5*math.pi)*rad2deg
