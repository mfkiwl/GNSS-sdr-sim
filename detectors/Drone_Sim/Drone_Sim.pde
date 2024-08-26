import grafica.*;


Vector[] realPosHistory = new Vector[64];
Vector[] spoofedPosHistory = new Vector[64];
int historyIndex = 0;
int historySubIndex = 0;

int accNPoints = 64;
GPointsArray accPointsX = new GPointsArray(accNPoints);
GPointsArray accPointsY = new GPointsArray(accNPoints);
GPlot plot;

Vector realPos = new Vector(50, 50);
Vector realVel = new Vector(0, 0);


Vector zone = new Vector(180, 180);
float zoneWidth = 20;
float zoneHeight = 20;

long lastTime;

float pid_p = 1;
float pid_i = 0;//.00001;
float pid_d = 50;
float windFactor = 0.1;
float maxForce = 100;

IIRFilter lowpass = lowPassFilter();
float angle = 0;

void setup() {
  size(720, 360*2); 
  noStroke();
  rectMode(CENTER);
  lastTime = millis();
  setupDroneControl();
  for(int i = 0; i<realPosHistory.length; i++) {
    realPosHistory[i] = new Vector(realPos.x, realPos.y);
    spoofedPosHistory[i] = new Vector(realPos.x, realPos.y);
  }
  
  plot = new GPlot(this, 0, 360);
  plot.setTitleText("inteneded acceleration of drone");
  plot.getXAxis().setAxisLabelText("time ms");
  plot.getYAxis().setAxisLabelText("force");
  plot.setDim(260, 260);
  plot.addLayer("X", accPointsX);
  plot.addLayer("Y", accPointsY);
  plot.getLayer("Y").setLineColor(color(100, 255, 100));
  
}


void draw() {
  println("draw");
  background(230);
  
  // decide time step
  long currentTime = millis();
  long deltaTms = currentTime - lastTime;
  lastTime = currentTime;
  float deltaT = deltaTms/1000.0f;
  deltaT = deltaT<0.1 ? deltaT : 0.1;
  
  float droneMass = 1;
  
  
  //angle = zone.sub(realPos).angle(new Vector(0, 1));
  angle = realVel.angle(new Vector(0, 1));
  
  //angle = lowpass.filter(angle);
  
  // decide spoofed position
  Vector simPos = mapPosition(realPos, zone, realVel, true);
  
  Vector target = new Vector();
  Vector force = new Vector();
  Vector PID_Force = new Vector();
  
  if (mouseX>0 && mouseX<360 && mouseY>0 && mouseY<360) {
    
    target = new Vector(mouseX, mouseY);
    
    // let drone chose how to move
    force = getDroneThrust(simPos, target);
    PID_Force = new Vector(force.x, force.y);
    
    // update real position
    float vel = realVel.length();
    if (vel>1) {
      float windForce = windFactor*vel*vel;
      force = force.sub(realVel.div(vel).mult(windForce));
    }
    
    // track position hisory
    realVel = realVel.add(force.mult(droneMass*deltaT));
    realPos = realPos.add(realVel.mult(deltaT));
    
    if (historySubIndex==4) {
      historySubIndex = 0;
      realPosHistory[historyIndex].x = realPos.x;
      realPosHistory[historyIndex].y = realPos.y;
      spoofedPosHistory[historyIndex].x = simPos.x;
      spoofedPosHistory[historyIndex].y = simPos.y;
      historyIndex = (historyIndex+1)%realPosHistory.length;
      if(accPointsX.getNPoints()<64) {
        accPointsX.add(currentTime, force.x);
        accPointsY.add(currentTime, force.y);
      } else {
        accPointsX.setXY(historyIndex, currentTime, force.x);
        accPointsY.setXY(historyIndex, currentTime, force.y);
      }
    } else { historySubIndex++; }
    
  }
  
  // draw on screen
  fill(255, 127);
  circle(mouseX, mouseY, 10);
  
  stroke(0);
  strokeWeight(5);
  line(360, 0, 360, 360);
  strokeWeight(1);
  noStroke();
  drawGrid(20, 10);
  drawHistorys();
  
  fill(255, 204);
  circle(simPos.x, simPos.y, 10);
  rect(zone.x, zone.y, zoneWidth, zoneHeight);
  
  fill(255, 204);
  circle(realPos.x+360, realPos.y, 10);
  rect(zone.x+360, zone.y, zoneWidth, zoneHeight);
  stroke(30, 255, 80, 255);
  strokeWeight(3);
  /*line(simPos.x, simPos.y, simPos.x+PID_Force.x, simPos.y+PID_Force.y);
  stroke(200, 100, 10, 255);
  strokeWeight(3);
  line(simPos.x, simPos.y, simPos.x+realVel.x, simPos.y+realVel.y);
  
  Vector realAcc = force.mult(droneMass*deltaT);
  stroke(255, 0, 0, 255);
  strokeWeight(3);
  line(simPos.x, simPos.y, simPos.x+realAcc.x*50, simPos.y+realAcc.y*50);
  noStroke();*/
  
  fill(0);
  textSize(16);
  /*text("Force:", 200, 20);
  text(force.x, 260, 20);
  text(force.y, 320, 20);
  
  text("Vel:", 200, 40);
  text(realVel.x, 260, 40);
  text(realVel.y, 320, 40);
  
  text("posDel:", 200, 60);
  text(target.sub(simPos).x, 260, 60);
  text(target.sub(simPos).y, 320, 60);*/
  
  plot.setPoints(accPointsX, "X");
  plot.setPoints(accPointsY, "Y");
  plot.defaultDraw();
}

void drawLine(Vector start, Vector end, int k) {
  Vector step = end.sub(start).div(k);
  for(int i=0; i<k-1; i++) {
    Vector a = start.add(step.mult(i));
    Vector b = a.add(step);
    line(a.x+360, a.y, b.x+360, b.y);
    a = mapPosition(a, zone);
    b = mapPosition(b, zone);
    line(a.x, a.y, b.x, b.y);
  }
}

void drawGrid(int n, int k) {
  stroke(80, 60, 230, 100);
  for(int i = 0; i<n; i++) {
    drawLine(new Vector(0, 360/n*i), new Vector(360, 360/n*i), n*k);
  }
  for(int i = 0; i<n; i++) {
    drawLine(new Vector(360/n*i, 0), new Vector(360/n*i, 360), n*k);
  }
  noStroke();
}

void drawHistorys() {
  stroke(0, 0, 0, 200);
  Vector a = realPosHistory[historyIndex];
  for(int i = 1; i<realPosHistory.length; i++) {
    Vector b = realPosHistory[(historyIndex+i)%realPosHistory.length];
    line(a.x+360, a.y, b.x+360, b.y);
    a=b;
  }
  a = spoofedPosHistory[historyIndex];
  for(int i = 1; i<spoofedPosHistory.length; i++) {
    Vector b = spoofedPosHistory[(historyIndex+i)%realPosHistory.length];
    line(a.x, a.y, b.x, b.y);
    a=b;
  }
  noStroke();
}
