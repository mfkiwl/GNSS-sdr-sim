// gps spoof location determination, uncomment methode you want to use

float angle_animation=0;

Vector mapPosition(Vector realPos, Vector zone) {
  return mapPosition(realPos, zone, new Vector(), false);
}



/*########################################
# offset move, with sideways direction 1 #
########################################*/
/*
Vector offset = new Vector(0, 0);
Vector groundVel = new Vector(0,0);

Vector mapPosition(Vector realPos, Vector zone, Vector realVel, boolean isDrone) {
  
  if(isDrone) {
    Vector dir = realPos.sub(zone);
    float dist = dir.length();
    
    float radius = 150;
    
    if(dist < radius) {
      float power = (1/(pow(dist/radius, 1.2))-1)*20;
      //power = 10;
      println(power);
      
      Vector force = dir.div(dist).mult(power/30);
      
      float angle = force.angle(realVel);
      float a2 = (angle/PI*180+360)%360-180;
      float minForceAngle = 60;
      if(abs(a2)<minForceAngle) {
        println(a2);
        force = force.rotate((minForceAngle-a2)/180*PI);
      }
      groundVel = groundVel.add(force).mult(0.8);
      offset = offset.add(groundVel.div(30));
    } else if(offset.length()>0.1){
      offset = offset.sub(offset.norm().div(10));
    }
  }
  
  return realPos.sub(offset);
}*/


/*########################################
# offset move, with sideways direction 2 #
########################################*/
Vector offset = new Vector(0, 0);

Vector mapPosition(Vector realPos, Vector zone, Vector realVel, boolean isDrone) {
  
  if(isDrone) {
    Vector dir = realPos.sub(zone);
    float dist = dir.length();
    
    if(dist < 100) {
      float power = (1/(pow(dist/100, 0.1))-1)*80;
      //power = 10;
      
      Vector force = dir.div(dist).mult(power/60);
      
      float angle = force.angle(realVel);
      float a2 = (angle/PI*180+360)%360-180;
      println(a2);
      float minForceAngle = 60;
      if(abs(a2)<minForceAngle) {
        force = force.rotate((minForceAngle-a2)/180*PI);
      }
      offset = offset.add(force);
    } else if(offset.length()>0.1){
      offset = offset.sub(offset.norm().div(10));
    }
  }
  
  return realPos.sub(offset);
}

/*####################
# Reconfiguring skew #
####################*/
/*float rangerange;
boolean isInRange = false;
float fixed_angle = 0;
Vector enterPos;
float enterAngle;
Vector transformOffset = new Vector(0,0);

Vector mapPosition(Vector realPos, Vector zone, Vector realVel, boolean isDrone) {
  
  float size = 15;
  float offset = 50;
  float range = 100;
  
  Vector dir = realPos.sub(zone);
  
  float angle = realVel.angle(new Vector(0, 1));
  //angle+=PI/16;
  
  dir = dir.rotate(fixed_angle);
  float dist = dir.length();
  
  
  
  if(isDrone) {
    if (dist<range+size/2 && !isInRange) {
      isInRange = true;
      println("enter range");
      fixed_angle = dir.angle(realVel)>0 ? angle-PI/4 : angle+PI/4;
      
      enterPos = realPos;
      enterAngle = angle;
    }
    if (dist>range+size/2+rangerange && isInRange) {
      isInRange = false;
      println("leaving range");
      fixed_angle = 0;
      transformOffset = new Vector(0,0);
    }
    
    if (isInRange) {
      //stroke(255, 255, 0);
      //strokeWeight(2);
      //line(enterPos.x, enterPos.y, enterPos.x+(range+size)*sin(enterAngle), enterPos.y+(range+size)*cos(enterAngle));
      //noStroke();
      
      if(abs(fixed_angle-angle)<0.2 & realVel.length() > 1) {
        println("danger direction");
        Vector currentPos = skewVectors(realPos.sub(zone), fixed_angle, range, size, offset);
        
        fixed_angle = dir.angle(realVel)>0 ? angle-PI/4 : angle+PI/4;
        enterPos = realPos;
        enterAngle = angle;
        
        Vector newPosOffset = skewVectors(realPos.sub(zone), fixed_angle, range, size, offset);
        
        transformOffset = currentPos.sub(newPosOffset);
      }
      
      if(realPos.sub(zone).length()<0.8*offset) {
        println("to close");
      }
    }
  }
  
  return realPos.add(skewVectors(realPos.sub(zone), fixed_angle, range, size, offset)).add(transformOffset);
  
}

Vector skewVectors(Vector relPos, float angle, float range, float size, float offset) {
  relPos = relPos.rotate(angle);
  float dist = relPos.length();
  if(abs(relPos.x)<range+size/2 && abs(relPos.y)<range+size/2) {
    
    float sa = sigmoid(-range-size/2, -size/2, size/2, range+size/2, relPos.x);
    float sb = sigmoid(-range-size/2, -size/2, size/2, range+size/2, relPos.y);
    //sb = dir.y<0 ? sb : -sb;
    
    return new Vector(0, sa*sb*offset).rotate(-fixed_angle);
  } else {
    return new Vector(0,0);
  }
}*/


/*##########################
# overlapping sigmoid skew #
##########################*/
/*Vector mapPosition(Vector realPos, Vector zone, Vector realVel, boolean isDrone) {
  
  float size = 15;
  float offset = 30;
  float range = 100;
  
  Vector dir = realPos.sub(zone);
  float angle = 0;//realVel.angle(new Vector(1, 1));
  //angle = angle_animation;
  //angle_animation += 0.000001;
  //if(angle_animation>2*PI) {angle_animation-=2*PI;}
  //println(angle);
  //angle = 0;
  dir = dir.rotate(angle);
  float dist = dir.length();
  if(abs(dir.x)<range+size/2 && abs(dir.y)<range+size/2) {
    
    float sa = sigmoid(-range-size/2, -size/2, size/2, range+size/2, dir.x);
    float sb = sigmoid(-range-size/2, -size/2, size/2, range+size/2, dir.y);
    sb = dir.y<0 ? sb : -sb;
    
    return realPos.add(new Vector(0, sa*sb*offset).rotate(-angle));
  } else {
    return realPos;
  }
  
}*/


float sigmoid(float x) {
  if(x < -1) {return 0;}
  if(x > 1 ) {return 1;}
  return (-(x-sqrt(3))*(x+sqrt(3))*x)/4+0.5;
}

float sigmoid(float off, float on, float x) {
  return sigmoid( (x - (on+off)/2) / (on-off) * 2 );
}

float sigmoid(float off1, float on1, float on2, float off2, float x) {
  return x < on2 ? sigmoid(off1, on1, x) : sigmoid(off2, on2, x);
}

/*##########################
#       ditance push       #
##########################*/
/*Vector mapPosition(Vector realPos, Vector zone, Vector realVel, boolean isDrone) {
  
  Vector dir = realPos.sub(zone);
  float dist = dir.length();
  float range = 80;
  if(dist<range) {
    //Vector offset = new Vector(0,(range-dist)/2);
    Vector offset = new Vector(0,sin((range-dist)/(dist)*PI)*(((range-dist))/2));
    if(realPos.y>zone.y) {
      return realPos.sub(offset);
    } else {
      return realPos.add(offset);
    }
  } else {
    return realPos;
  }
  
}*/

/*############################################################
# V1 push away from center, by faking being closer to center #
############################################################*/
/*Vector mapPosition(Vector realPos, Vector zone, Vector realVel, boolean isDrone) {
  
  Vector dir = realPos.sub(zone);
  float dist = dir.length();
  float range = 80;
  if(dist<range) {
    return realPos.sub(dir.div(dist).mult(pow(range-dist, 0.9)));
  } else {
    return realPos;
  }
  
}*/
