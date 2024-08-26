// filter to combine acceleration data and, gps data. based on calman filter but does not track distributions

class KalmanFilter {
  Vector pos;
  Vector vel;
  
  public KalmanFilter() {
    pos = new Vector();
    vel = new Vector();
  }
  
  public Vector predict(Vector acc, float dt) {
    vel = vel.add(acc.mult(dt));
    pos = pos.add(vel.mult(dt));
    return pos;
  }
  
  public Vector getPos() { return pos; }
  public Vector getVel() {return vel; }
  
  public void update(Vector pos, Vector vel) {
    float newPosWeight = 0.5;
    Vector newPos = this.pos.mult((1-newPosWeight)).add(pos.mult(newPosWeight));
    Vector accError = this.pos.sub(newPos);
    println(accError); // majority of this error comes from predicting position
    
    if(accError.length()>1) {
      println("Spoofing detected");
    }
    
    fill(255, pow(accError.length(), 4)*10);
    circle(newPos.x, newPos.y, 12);
    
    this.pos = newPos;
    
    float newVelWeight = 0.5;
    this.vel = this.vel.mult((1-newVelWeight)).add(vel.mult(newVelWeight));
    
  }
}
