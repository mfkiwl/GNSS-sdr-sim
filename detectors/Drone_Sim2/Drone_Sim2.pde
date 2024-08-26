Drone drone;
Vector lastAcc;
public Queue<Vector> posHist;
public Queue<Vector> velHist;
public Queue<Vector> spoofPosHist;
public Queue<Vector> spoofVelHist;

public Vector lastSpoofPos = new Vector(0, 0);

int round = 0;

void setup() {
  drone = new Drone();
  // set path drone needs to follow
  drone.path.add(new Vector(100, 100));
  drone.path.add(new Vector(200, 50));
  drone.path.add(new Vector(50, 200));
  drone.path.add(new Vector(200, 200));
  
  lastAcc = new Vector(0,0);
  posHist = new ArrayDeque<Vector>(25);
  velHist = new ArrayDeque<Vector>(25);
  
  spoofPosHist = new ArrayDeque<Vector>(12);
  spoofVelHist = new ArrayDeque<Vector>(12);
  
  size(720, 360); 
}

// settings for signal processing/generation/travel delays
int droneRate = 100;//hz
int gpsRate = 20;//hz
float gpsDelay = 0.2;//s
float spoofDelay = 0.1;//s

void draw() {
  //background(200);
  
  float dt = 1.0/droneRate;
  
  // keep track of the position history of the drone
  posHist.add(drone.getPosition());
  velHist.add(drone.getVelocity());
  if(posHist.size()>gpsDelay*droneRate) {
    posHist.remove();
    velHist.remove();
  }
  
  // control loop of drone and physiscs/movement simulation
  Vector force = drone.controllLoop(lastAcc, dt);
  drone.applyForce(force);
  drone.windResistence(0.0025);
  lastAcc = drone.tick(dt);
  
  // spoofing intermittent gps updates
  round++;
  if(round==5) {
    round=0;
    
    Pair<Vector, Vector> spoofPosVel = getSimPosVel(posHist.peek(), velHist.peek(), spoofDelay);
    spoofPosHist.add(spoofPosVel.a);
    spoofVelHist.add(spoofPosVel.b);
    lastSpoofPos = spoofPosVel.a;
    //spoofPosHist.add(posHist.peek().add(velHist.peek().mult(spoofDelay)));
    //spoofVelHist.add(velHist.peek());
    
    // give the spoofed GPS position
    //drone.updateGPSPos(posHist.peek(), velHist.peek());
    drone.updateGPSPos(spoofPosHist.peek(), spoofVelHist.peek());
    
    if(spoofPosHist.size()>spoofDelay*gpsRate) {
      spoofPosHist.remove();
      spoofVelHist.remove();
    }
    
  }
  
  // draw
  noStroke();
  
  fill(255, 0, 0);
  circle(drone.getPosEstimate().x, drone.getPosEstimate().y, 10);
  
  fill(0, 255, 0);
  circle(drone.getPosition().x, drone.getPosition().y, 10);
  
  //fill(255, 255, 0);
  //circle(lastSpoofPos.x, lastSpoofPos.y, 10);
  
  fill(0, 0, 255);
  circle(drone.path.peek().x, drone.path.peek().y, 10);
}
