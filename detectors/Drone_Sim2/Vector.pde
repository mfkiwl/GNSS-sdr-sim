// 2D Vector data, and functions
class Vector {
  public float x, y;
  Vector() {
    this.x = 0;
    this.y = 0;
  }
  Vector(float x, float y) {
    this.x = x;
    this.y = y;
  }
  float length() {
    return sqrt(x*x+y*y);
  }
  Vector add(Vector that) {
    return new Vector(this.x+that.x, this.y+that.y);
  }
  Vector sub(Vector that) {
    return new Vector(this.x-that.x, this.y-that.y);
  }
  Vector mult(float v) {
    return new Vector(this.x*v, this.y*v);
  }
  Vector div(float v) {
    return new Vector(this.x/v, this.y/v);
  }
  float dot(Vector that) {
    return this.x*that.x + this.y*that.y;
  }
  float cross(Vector that) {
    return this.x*that.y-this.y*that.x;
  }
  Vector rotate(float angle) {
    return new Vector(cos(angle)*x-sin(angle)*y, sin(angle)*x+cos(angle)*y);
  }
  Vector rotateAround(float angle, Vector point) {
    return this.sub(point).rotate(angle).add(point);
  }
  float angle(Vector that) {
    return atan2(this.cross(that), this.dot(that));
  }
  Vector norm() {
    return this.div(this.length());
  }
  Vector limitLen(float len) {
    if (length()>len) {
      return norm().mult(len);
    } else {
      return this;
    }
  }
  
  boolean hasNaN() {
    return Float.isNaN(x) || Float.isNaN(y);
  }
  
  @Override
  String toString() {
    return "["+x+", "+y+"]";
  }
}
