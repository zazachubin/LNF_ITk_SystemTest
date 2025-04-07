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

//--------------------------------------------------------------------------------
//@private members
//--------------------------------------------------------------------------------

