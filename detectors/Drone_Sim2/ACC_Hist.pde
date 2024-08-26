// history of acceleration used to correct look back at effect of acceleration over a short time since gps reciver needs processing time.
class ACC_Hist {
  
  private Vector[] values;
  int index;
  
  
  public ACC_Hist(int delay) {
    values = new Vector[delay];
    for(int i=0; i<values.length; i++) {
      values[i] = new Vector();
    }
    index = 0;
  }
  
  public Vector filter(Vector in) {
    values[index] = in;
    index = (index+1)%values.length;
    return values[(index-1+values.length)%values.length];
  }
  
  public Vector getMovement(Vector pos, Vector vel, float dt) {
    for(int i=0; i<values.length; i++) {
      int j=(i+index)%values.length;
      vel = vel.add(values[j].mult(dt));
      pos = pos.add(vel.mult(dt));
    }
    return pos;
  }
  
}
