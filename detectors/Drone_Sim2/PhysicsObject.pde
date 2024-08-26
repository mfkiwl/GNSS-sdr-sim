// object whith position, velocity, and mass that fores can be applied to
class PhysicsObject {
  private float mass;
  private Vector pos;
  private Vector vel;
  private Vector force;
  
  public PhysicsObject(float mass, Vector pos) {
    this.mass = mass;
    this.pos = pos;
    vel = new Vector(0,0);
    force = new Vector(0,0);
  }
  
  public void applyForce(Vector f) {
    force = force.add(f);
  }
  
  public void windResistence(float a) {
    applyForce(vel.mult(-a*vel.length()));
  }
  
  public Vector tick(float dt) {
    Vector acc = force.div(mass);
    vel = vel.add(acc.mult(dt));
    pos = pos.add(vel.mult(dt));
    force = new Vector(0,0);
    return acc;
  }
  
  public Vector getPosition() {
    return pos;
  }
  
  public Vector getVelocity() {
    return vel;
  }
  
}
