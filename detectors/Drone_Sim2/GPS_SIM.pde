// calculate the position that should be spoofed


//float spoofDuration = 0;

Vector Zone = new Vector(200, 200);

Vector spoofPos = new Vector();
Vector spoofVel = new Vector();

PhysicsObject shift = new PhysicsObject(1, new Vector(0,0));

// linear
Pair<Vector, Vector> getSimPosVel(Vector pos, Vector vel, float delay) {
  Vector velNorm = vel.norm();
  float pushPointOffset = 30;
  // where/what direction to apply force from
  Vector pushPoint = (velNorm.hasNaN() ? pos.sub(Zone).limitLen(pushPointOffset).add(Zone)/*in between zone and pos?*/ : Zone.sub(velNorm.mult(pushPointOffset)));
  
  // predictaed futore position of drone to apply the force at
  Vector predPos = pos.add(vel.mult(delay));
  
  //return new Pair<>(predPos, vel);/*
  
  // unit length force in corect direction
  Vector forceUnit = predPos.sub(pushPoint);
  float dist = forceUnit.length();
  forceUnit = forceUnit.div(dist);
  
  // magnatude of force to apply
  float forceMag = min(1.0/pow(dist/20, 2), 1) * 25;
  
  // see effect of force over time between two gps updates.
  shift.applyForce(forceUnit.mult(forceMag));
  shift.windResistence(0.01);
  shift.tick(1.0/gpsRate);
  //print(shift.getPosition());
  //println(shift.getVelocity());
  
  // final spoofed position and velocity
  //Vector simPos = pos.add(vel.mult(delay)).add(new Vector(spoofDuration*5, -spoofDuration*2));
  Vector simPos = predPos.sub(shift.getPosition());
  Vector simVel = vel.sub(shift.getVelocity());
  
  
  //spoofDuration += 0.05;
  
  
  
  // draw
  fill(255, 255, 255);
  circle(Zone.x, Zone.y, 10);
  
  fill(150, 150, 150);
  circle(pushPoint.x, pushPoint.y, 10);
  
  return new Pair<>(simPos, simVel);/**/
}
