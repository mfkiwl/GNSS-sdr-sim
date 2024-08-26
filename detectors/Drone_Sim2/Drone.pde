import java.util.Queue;
import java.util.ArrayDeque;

float pid_p = 1;
float pid_i = 0;
float pid_d = 100;

float maxForce = 100;

// represent the drone
class Drone extends PhysicsObject{
  
  MiniPID pidX = new MiniPID(pid_p, pid_i, pid_d);
  MiniPID pidY = new MiniPID(pid_p, pid_i, pid_d);
  KalmanFilter filter;
  ACC_Hist acc_delay;
  
  public Queue<Vector> path;
  float pointReachedRange;
  
  Vector predPos;
  
  public Drone() {
    super(1, new Vector(50, 50));
    predPos = getPosition();
    path = new ArrayDeque<Vector>(10);
    pointReachedRange = 10;
    filter = new KalmanFilter();
    acc_delay = new ACC_Hist((int)(100*0.2));
  }
  
  // return the next target location the drone needs to move to
  private Vector checkTarget() {
    if (path.size()==0) {
      return new Vector();
    }
    if (path.size()==1) {
      return path.peek();
    }
    if(path.peek().sub(getPosEstimate()).length()<pointReachedRange) {
      path.remove();
    }
    return path.peek();
  }
  
  // 100 hz
  public Vector controllLoop(Vector acc, float dt) {
    acc = acc_delay.filter(acc);
    Vector pos = filter.predict(acc, dt);
    pos = acc_delay.getMovement(filter.getPos(), filter.getVel(), dt);
    predPos = pos;
    
    Vector target = checkTarget();
    
    Vector force = new Vector(
      (float) pidX.getOutput(pos.x, target.x),
      (float) pidY.getOutput(pos.y, target.y)
    );
    
    if (force.length()>maxForce) {
      force = force.div(force.length()).mult(maxForce);
    }
    
    return force;
  }
  
  // 20 hz
  // 0.2 expected delay + 0.4 fake delay
  public void updateGPSPos(Vector pos, Vector vel) {
    filter.update(pos, vel);
  }
  
  public Vector getPosEstimate() {
    return predPos;
  }
  
  
}
