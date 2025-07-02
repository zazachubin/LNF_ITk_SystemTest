// $License: NOLICENSE
//--------------------------------------------------------------------------------
/**
  @file $relPath
  @copyright $copyright
  @author felix
*/

//--------------------------------------------------------------------------------
// Libraries used (#uses)

//--------------------------------------------------------------------------------
// Variables and Constants


//--------------------------------------------------------------------------------
//@public members
//--------------------------------------------------------------------------------
public float ConvAdc2Temp(float adc_chan, uint precision)
{
  float tn = 298.15;
  float b = 3435.0;

   // 32767 corresponds to -273.15degC while 32766 to -116.43degC
   if (0<adc_chan & adc_chan<32760)
   {
     //DebugN("adc_chan<32760",adc_chan);
     float adc_to_degree = 1.0/(log(1./(32767./adc_chan-1))/b+1/tn)-273.15;
     //DebugN("Temp in degC = ", adc_to_degree);
     return adc_to_degree;
   }
   else {
     float adc_to_degree=adc_chan;
     //DebugN("adc_to_degree>32760",adc_to_degree);
     return -999;
   }
}

public double NTC_10K_formula(double R)
{
  double A = 1.098012950e-03;
  double B = 2.391408415e-04;
  double C = 0.7500259398e-07;

  double logR2 = log(R);
  double T = (1.0 / (A + B*logR2 + C*logR2*logR2*logR2));
  double Tc = T - 273.15;
  return Tc;
}

public double module_NTC_10K_formula(double R)
{
  double A = 1.103026059e-03;
  double B = 2.203809745e-04;
  double C = 2.831203056e-07;

  double logR2 = log(R);
  double T = (1.0 / (A + B*logR2 + C*logR2*logR2*logR2));
  double Tc = T - 273.15;
  return Tc;
}

public double ConvAdc2NTC_Res(float adc_chan)
{
  double Vout = 2.5/32767.0 * adc_chan;
  double Rntc = Vout * 10000/(2.5 - Vout);
  return Rntc;
}

public float dewPoint_formula(float DPv)
{
  float chamber_DewPoint = ((DPv-2.016) / 0.0192) - 2.434;
  return chamber_DewPoint;
}

//--------------------------------------------------------------------------------
//@private members
//--------------------------------------------------------------------------------

