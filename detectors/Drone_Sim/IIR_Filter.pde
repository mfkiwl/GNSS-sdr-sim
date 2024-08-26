class IIRFilter {
  float[] a;
  float[] b;
  
  float[] x;
  float[] y;
  
  IIRFilter(float[] b, float[] a) {
    this.a = a;
    this.b = b;
    x = new float[b.length];
    y = new float[a.length];
  }
  
  float filter(float v) {
    y[0] = 0;
    x[0] = v;
    for(int i=0; i<b.length; i++) {
      y[0] += b[i]*x[i];
    }
    for(int i=1; i<a.length; i++) {
      y[0] += a[i]*y[i];
    }
    y[0] /= a[0];
    
    for(int i=1; i<x.length; i++) {
      x[i] = x[i-1];
    }
    for(int i=1; i<y.length; i++) {
      y[i] = y[i-1];
    }
    
    return y[0];
  }
  
}

IIRFilter lowPassFilter() {
  return new IIRFilter(new float[] {0.29289322, 0.58578644, 0.29289322}, new float[]{ 1.00000000e+00, -1.11022302e-16,  1.71572875e-01});
}
