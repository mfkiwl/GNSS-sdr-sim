// normal controle for the drone

MiniPID pidX = new MiniPID(pid_p, pid_i, pid_d);
MiniPID pidY = new MiniPID(pid_p, pid_i, pid_d);

void setupDroneControl() {
  pidX.setOutputLimits(maxForce);
  pidY.setOutputLimits(maxForce);
}

Vector getDroneThrust(Vector position, Vector target){
  // given target (mouse) and drone position (GPS), caculate force
    
    Vector distance = position.sub(target);
    
    Vector force = new Vector(
      (float) pidX.getOutput(distance.x, 0),
      (float) pidY.getOutput(distance.y, 0)
    );
    
    if (force.length()>maxForce) {
      force = force.div(force.length()).mult(maxForce);
    }
    return force;
}
