/* 
Program to convert bin list data to castor histogram cdf. It takes a data file and output file containing 
the cdf including those derived from rotating the system through three angles. 


 Last edited Apr 24, 2020
 
 // Title            :   phytoPETtoCastorHistogram.cc
 // Date             :   April, 14 2020
 // Author           :   J Nsofini
 // Version          :   1.1
 // Description      :   Convertion of bin PET file to castor-recon histogram cdf
 // Last Edit        : 
 // Options          : 

 last edits:
 Added: 

 Features of the program:
 This is a naive version, it runs through the datafile twice. The first time it opens a temporal datafile and
 stores the data in it as it reads it. And the the histogram data is ready, it reads the file and then create 
 the output data file.

 WOrking Code!

Apr 24
Modified to take into account the radiation decay.
p = A/A_0 = e^{- lambda t} = e^{-t/t1/2 * ln2}

*/


#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <stdlib.h>
#include <math.h>

std::string outname = "";
std::string inname = "";

int e_min = 408; //default limit for energy cut -20% +60% of 511 keV;
int e_max = 818;
bool filter = false; //filtering flag for limiting the angle of lines of response
float LAMDA_C = 4.56229e6;    //ln(2) * HALF_LIFE = ln(2) * 109.7*60*1000 // msec

//---------------------------------------------------------------------------------

typedef struct 
{
  unsigned short x; unsigned short y; unsigned short e;
}RawData;

typedef struct 
{
  unsigned short mask;   //tells which modules where involved in the event
  short nData;                 //tells how many modules where involved in the event
  std::vector<short> id;
} Coincidence;


void Usage(void);
void ParseCommandLineArguments(int narg, char* argv[]);


RawData GetData(std::fstream *fs);
Coincidence GetCoincidence(std::fstream *fs);
long int GetTime(std::fstream *fs);
void WriteCASTORdata(std::fstream *fs, Coincidence co, RawData *data, unsigned int tt, int rot_index, int v_index);
short GetAngle(std::fstream *fs);
short GetHeight(std::fstream *fs);
void InitializeFile(std::fstream *fs);

int main(int argc,char *argv[])
{  
  ParseCommandLineArguments(argc, argv);
 
  Coincidence coinc;
  RawData data[4];
  unsigned long int time=0;
  // int time_cycle  = 0;
  unsigned long int t0 = 0;
  // unsigned long int tt = 0;
  // unsigned long int prev_t = 0;
  int rot_index   = 0;
  char rot_step  = 30; //angluar value of rotational step in degrees;
  int v_index = 0;
  int v_step = 48; //heght of vertical step of the stage in mm;
  unsigned long int written_event_counter = 0;  //number of events written to CDF file
  unsigned long int counter = 0;  //number of events read from BIN file
  //unsigned long int counts_on_0 = 0, counts_on_1 = 0, counts_on_2 = 0; // Counts the event per rotation
  //unsigned long int written_event_on_0 = 0, written_event_on_1 = 0, written_event_on_2 = 0 ;       //counts written events per rotation

  // Create file first by simple open and close
  std::fstream createfile(outname.data(), std::ios::out | std::ios::binary); // open for writing firs
  InitializeFile(&createfile);
  createfile.close(); // open for writing first

  //open the file for reading and writing
  std::fstream outFile;

  outFile.open(outname.data(), std::ios::out | std::ios::binary);

  // std::ofstream outAscii;
  // outAscii.open("data.txt");
  
  std::fstream inFile;
  inFile.open(inname.data(), std::ios::in | std::ios::binary);
  
  if(!inFile.is_open())  std::cerr<<"could not open "<<inname<<" "<<__FILE__<<" "<<__LINE__<<std::endl;


  while(inFile.good()) {
    
	  coinc = GetCoincidence(&inFile);
	  
	  if(inFile.eof())break;

	  // std::cout<<std::endl<<std::hex<<coinc.mask<<std::dec<<" "<<counter<<std::endl;

	  if(coinc.mask == 0xAAAA) {
    
      coinc = GetCoincidence(&inFile);
      //std::cout<<"GOT HERE"<<std::endl;
      //std::cout<<std::hex<<coinc.mask<<std::dec<<" "<<counter<<std::endl;
      // if(counter==1){exit(0);}
      
      if(coinc.mask == 0xAAAA) {
        rot_index++;
      } 	
	    else {
	  	  std::cerr<<"Abnormal event in input datafile... exiting"<<std::endl;
	  	  exit(-1);
	  	}
	  }

	  if(coinc.mask == 0xBBBB) {
      coinc = GetCoincidence(&inFile);
      if (coinc.mask == 0xBBBB){
        short angle = GetAngle(&inFile);
        rot_index = angle/rot_step;
        short height = GetHeight(&inFile);
    
        v_index = height/v_step;
        std::cout<< angle <<" r_ind ="<<rot_index<<" " << height <<" v_ind = " << v_index<<std::endl;  	  
	  	}
	      else	{
	  	  std::cerr<<"Abnormal in input datafile... exiting"<<std::endl;
	  	  exit(-2);
	  	}
	  }

	  //std::cout<<std::hex<<coinc.mask<<std::dec<<" ndata = "<<coinc.nData<<"  : ";
	 	  
	  for(int k = 0; k<coinc.nData; k++) {
      data[k]= GetData(&inFile); 
      //  std::cout<<" : "<<data[k].x<<" "<<data[k].y<<" "<<data[k].e<<" ";
	  }

	  time = GetTime(&inFile);
	  
	  counter++;
	  
	  if(t0==0) t0=time;
	  unsigned long int t = time-t0;     
	  unsigned long int t_msec = (unsigned int) ((t*4.)/1000000.0);
	  //if((t_msec/1000.0)>400.){ exit(-3);}
	  // std::cout<<time<<std::endl;
	  bool is_good_event = true;
	  for(int i=0; i<coinc.nData; i++) {
      if(data[i].e<e_min||data[i].e>e_max) is_good_event = false;
	  }
	  
	  if(coinc.nData == 2 && filter == true && is_good_event == true) {
	      if(abs(data[0].x-data[1].x)<3 && abs(data[0].y-data[1].y)<20){
        is_good_event = true;
        //	  std::cout<<data[0].x<<" "<<data[1].x<<std::endl;		
		  }
      else {
		    is_good_event = false;
		  }
	  }

	  if(is_good_event==true && coinc.nData==2 && coinc.id[1]-coinc.id[0] == 2){ // accept only specific pair of events

      // To reduce the data to 70% see page 44 #16 Desk III  for 85%[3121154,2849599,2591060] use this block

      /* if (rot_index==0 && written_event_on_0 < 2570362){
        WriteCASTORdata(&outFile, coinc, &data[0], t_msec, rot_index, v_index);
        written_event_counter++;
        written_event_on_0++;
      }
      if (rot_index==1 && written_event_on_1 < 2335247){
        WriteCASTORdata(&outFile, coinc, &data[0], t_msec, rot_index, v_index);
        written_event_counter++;
        written_event_on_1++;
      }
      if (rot_index==2 && counts_on_2 < 2133814){
        WriteCASTORdata(&outFile, coinc, &data[0], t_msec, rot_index, v_index);
        written_event_counter++;
        written_event_on_2++;
      } */
      WriteCASTORdata(&outFile, coinc, &data[0], t_msec, rot_index, v_index);
      written_event_counter++;

      // if (rot_index==0) counts_on_0++;
      // if (rot_index==1) counts_on_1++;
      // if (rot_index==2) counts_on_2++;
	    }
	  std::cout<<"\r run time = "<<t_msec/1000.0<<" sec ";
	  //std::cout<<": run time = "<<t_msec/1000.0<<" sec "<<std::endl;;
	}
    


  std::cout<<std::endl<<"There are: "<<written_event_counter<<" events were written to "<<outname<<std::endl;

  // std::cout<<"Events on rot 0: "<< counts_on_0 <<" written: "<< written_event_on_0 <<std::endl;
  // std::cout<<"Events on rot 1: "<< counts_on_1 <<" written: "<< written_event_on_1 <<std::endl;
  // std::cout<<"Events on rot 2: "<< counts_on_2 <<" written: "<< written_event_on_2 <<std::endl;

  // outAscii.close();
  outFile.close();
  inFile.close();
  return 0;
}
//----------------------------------------------------------------------------------------------------------

void InitializeFile(std::fstream *fs){
  int max_v_index = 0;
  unsigned int numCrystals1D = 35;
  unsigned int numDetectorsPerRing = 12;
  unsigned int numCrystalsPerModule = numCrystals1D*numCrystals1D;
  //int num_angular_pos = 3;
  unsigned int MaxCastorID = numDetectorsPerRing*numCrystalsPerModule + max_v_index*numDetectorsPerRing*numCrystalsPerModule;

  // Create dummy int and initialize the file with it
  unsigned int t = 0;
  for (size_t i = 0; i < MaxCastorID; i++)
  {
    fs->write((char *)&t, sizeof(int));
    fs->write((char *)&t, sizeof(float));
    fs->write((char *)&t, sizeof(int));
    fs->write((char *)&t, sizeof(int));
  }



 
}

//----------------------------------------------------------------------------------------------------------

short GetAngle(std::fstream *fs)
{
  char buffer[2]={0,0};
  short angle=0;
   
  fs->read(&buffer[0], 2);
  angle |= (buffer[0] << 8 ) | (buffer[1] & 0xff);
  return angle;
}

//----------------------------------------------------------------------------------------------------------

short GetHeight(std::fstream *fs)
{
  char buffer[2]={0,0};
  short h=0;
   
  fs->read(&buffer[0], 2);
  h |= (buffer[0] << 8 ) | (buffer[1] & 0xff);
  return h;
}

//----------------------------------------------------------------------------------------------------------

Coincidence GetCoincidence(std::fstream *fs)
{
  Coincidence coinc;
  short n = 0;
  char buffer[4]={0,0,0,0};

  // std::cout<<std::endl<<std::hex<<" b0 = "<<short (buffer[0]&0x00FF)<<", b2 = "<<short (buffer[2]&0x00FF)
  //  	   <<", b1 = "<<short (buffer[1]&0x00FF)<<", b3 =  "<<short (buffer[3]&0x00FF)<<std::endl;
  fs->read(&buffer[0], 2);

  buffer[2]=buffer[0];
  buffer[3]=buffer[1];

  // std::cout<<std::hex<<" b0 = "<<short (buffer[0]&0x00FF)<<", b2 = "<<short (buffer[2]&0x00FF)
  //  	   <<", b1 = "<<short (buffer[1]&0x00FF)<<", b3 =  "<<short (buffer[3]&0x00FF)<<std::endl;
  
  buffer[0] = buffer[0]&0xF0;
  buffer[0] = (buffer[0]>>4)&0x0F;
  buffer[2] = buffer[2]&0x0F;

  buffer[1] = buffer[1]&0xF0;
  buffer[1] = (buffer[1]>>4)&0x0F;
  buffer[3] = buffer[3]&0x0F;  

  // std::cout<<std::hex<<" b0 = "<<short (buffer[0]&0x00FF)<<", b2 = "<<short (buffer[2]&0x00FF)
  // 	   <<", b1 = "<<short (buffer[1]&0x00FF)<<", b3 =  "<<short (buffer[3]&0x00FF)<<std::endl;

   coinc.mask = (buffer[0] << 12 ) | (buffer[2] << 8) | (buffer[1] << 4) | (buffer[3]);
   // if(buffer[0]==0x0) std::cout<<0;

  
  if(buffer[0] == 0xF) {++n; coinc.id.push_back(1);}
  if(buffer[2] == 0xF) {++n; coinc.id.push_back(0);} 
  if(buffer[1] == 0xF) {++n; coinc.id.push_back(3);}
  if(buffer[3] == 0xF) {++n; coinc.id.push_back(2);}

  // if(buffer[0] == 0xF) {++n; coinc.id.push_back(1);} //detector numbering starts from 1
  // if(buffer[2] == 0xF) {++n; coinc.id.push_back(2);} 
  // if(buffer[1] == 0xF) {++n; coinc.id.push_back(3);}
  // if(buffer[3] == 0xF) {++n; coinc.id.push_back(4);}
					      
  coinc.nData = n;
  return coinc;
}

//----------------------------------------------------------------------------------------------------------

RawData GetData(std::fstream *fs)
{
  char buffer[6]={0,0,0,0,0,0};
  RawData data;
  short x1=0, y1=0, e1=0;
   
  fs->read(&buffer[0], 6);
  x1 |= (buffer[0] << 8 ) | (buffer[1] & 0xff);
  data.x = x1;
  y1 |= (buffer[2] << 8 ) | (buffer[3] & 0xff);
  data.y = y1;
  e1 |= (buffer[4] << 8 ) | (buffer[5] & 0xff);
  data.e = e1;

  return data;
}

//----------------------------------------------------------------------------------------------------------


long int GetTime(std::fstream *fs)
{
  char buffer[8]={0,0,0,0,0,0,0,0};
  unsigned long int time =0;
  unsigned long int temp[8]={0,0,0,0,0,0,0,0};
  fs->read(&buffer[0], 8);

  for(int i = 0; i<8; i++)
    {
      temp[i] = buffer[i] & 0x00000000000000ff;
    }

  time |= ((temp[0]<<56) & 0xff00000000000000);
  time |= ((temp[1]<<48) & 0x00ff000000000000);
  time |= ((temp[2]<<40) & 0x0000ff0000000000);
  time |= ((temp[3]<<32) & 0x000000ff00000000);
  time |= ((temp[4]<<24) & 0x00000000ff000000);
  time |= ((temp[5]<<16) & 0x0000000000ff0000);
  time |= ((temp[6]<<8)  & 0x000000000000ff00);
  time |= ((temp[7])     & 0x00000000000000ff);

  return time;
}

//----------------------------------------------------------------------------------------------------------

void WriteCASTORdata(std::fstream *fs, Coincidence co, RawData *data, unsigned int t, int rot_index, int v_index){
  /*
  Read and write to the castor data file.

  Input
  -----
  fs : io/out file stream 
  co : coincidence data object
  data  : pointer to read data
  tt    : time in msec
  rot_index : Current rotation
  v_index   : verticel height

  Return
  ------
  None

  */
  fs->write((char *)&t, sizeof(unsigned int));          //event time stamp in ms
  // float a = 0;                                      //Attenuation correction factor *optional*
  // fs->write((char *)&a, sizeof(float));
  // float s = 0;                                      //Un-normalized scatter intensity rate of the 
  // fs->write((char *)&s, sizeof(float));             //corresponding event (count/s) *optional*
  // float r = 0;                                      //Un-normalized random intensity rate of the
  // fs->write((char *)&r, sizeof(float));             //corresponding event (count/s) *optional*
  // float n = 0;                                      //Normalization factor of the corresponding 
  // fs->write((char *)&n, sizeof(float));             //event  *optional*
  // short k=co.nData-1;                               //Number of contributing crystal pairs
  // fs->write((char *)&k, sizeof(short));             //Mandtory if k>1

  unsigned int numCrystals1D = 35;
  unsigned int numDetectorsPerRing = 12;
  unsigned int numCrystalsPerModule = numCrystals1D*numCrystals1D;
  int num_angular_pos = 3;
  unsigned int castorID1 = 0;
  unsigned int castorID2 = 0;

  //Calculate the csator ID using the x and y coordinates of the event
  int det_id = co.id[0] + co.id[0]*(num_angular_pos - 1) + rot_index;
  castorID1 = data[0].x + data[0].y*numDetectorsPerRing*numCrystals1D + det_id*numCrystals1D + v_index*numDetectorsPerRing*numCrystalsPerModule;

  int det_id2 = co.id[1] + co.id[1]*(num_angular_pos - 1) + rot_index;	 
  castorID2 = data[1].x + data[1].y*numDetectorsPerRing*numCrystals1D + det_id2*numCrystals1D + v_index*numDetectorsPerRing*numCrystalsPerModule;

  // Seek location of the file to write this 
  fs->seekg( (3*sizeof(int) + sizeof(float))*(castorID1 + castorID2*numDetectorsPerRing) + sizeof(int));
  float p;
  fs->read((char*)& p, sizeof(float));
  p += exp(-LAMDA_C*t);

  //record these value and also display on commandline
  fs->write((char *)&p, sizeof(float));
  fs->write((char *)&castorID1, sizeof(int));
  fs->write((char *)&castorID2, sizeof(int));

  // for(int k=0; k<co.nData; k++){
            
  //   int det_id = co.id[k] + co.id[k]*(num_angular_pos - 1) + rot_index;
  //   // castorID1 = data[k].x + data[k].y*numDetectorsPerRing*numCrystals1D + co.id[k]*numCrystals1D;
  //   castorID1 = data[k].x + data[k].y*numDetectorsPerRing*numCrystals1D + det_id*numCrystals1D + v_index*numDetectorsPerRing*numCrystalsPerModule;
  //   // Read the p values:
  //   fs.seekg(sizeof(t) +sizeof(t) + sizeof(castorID1) + );
  //   fh.read((char*)& v, sizeof(Data));
  //   fs->write((char *)&castorID1, sizeof(unsigned int));
  //   // for(int l=i+1; l<co.nData; l++)
  //   // 	 {
  //   // 	   unsigned int castorID2 = numCrystalsPerModule*co.id[l]+data[l].x+numCrystals*data[l].y;
  //   // 	   //std::cout<<castorID<<" "<<co.id[i]<<" "<<data[i].x<<" "<<data[i].y<<" "<<data[i].e<<std::endl;
  //   // 	   fs->write((char *)&castorID2, sizeof(unsigned int));
  //   // 	 }
  //   }
}


//----------------------------------------------------------------------------------------------------------------------------------
// ParseCommandLineArguments
//----------------------------------------------------------------------------------------------------------------------------------
void ParseCommandLineArguments(int narg, char* argv[])
{
  if(narg<1)Usage();

  for(int i=1; i<narg; i++)
    {
      std::string arg = argv[i];
      if(arg=="-h" || arg=="--help")
        {
          Usage();
        }
      else if(arg=="-inF")
        {
          if(i==narg-1)
            { std::cout<<"-inF requires one argument!"<<std::endl;  Usage(); }

          inname = argv[i+1];
        }
      else if(arg=="-outF")
        {
          if(i==narg-1)
            { std::cout<<"-outF requires one argument!"<<std::endl;  Usage(); }

          outname = argv[i+1];
        }
      else if(arg=="-filter")
        {
          filter = true;
        }
      else if(arg=="-minE")
        {
          if(i==narg-1)
            { std::cout<<"-minE requires one argument!"<<std::endl;  Usage(); }

          e_min = 511.*(1. - atof(argv[i+1])/100.);
        }
      else if(arg=="-maxE")
        {
          if(i==narg-1)
            { std::cout<<"-maxE requires one argument!"<<std::endl;  Usage(); }

          e_max = 511.*(1. + atof(argv[i+1])/100.);
        }

    }

  if(outname==""||inname=="")
    {
      Usage();
    }

  std::cout<<" Input file name = "<<inname<<std::endl;
  std::cout<<" Output file name = "<<outname<<std::endl;

}


//-------------------------------------------------------------------------------------------------------------------------------
// ParseCommandLineArguments: Takes the aguments sent via the command line and analyse them and send out corresponding messages.
//-------------------------------------------------------------------------------------------------------------------------------

void Usage(void)
{
  std::cout<<std::endl;
  std::cout<<"Usage:"<<std::endl;
  std::cout<<"      exec_name: -inF phytoPET_data.bin -outF CASTOR_data.cdf -minE 20 -maxE 60"<<std::endl;
  std::cout<<std::endl;
  std::cout<<"  options:"<<std::endl;
  std::cout<<" -h                      print this help message"<<std::endl;
  std::cout<<" -inF  phytoPET_data.bin provide the name of input_data_file (required)"<<std::endl;
  std::cout<<" -outF CASTOR_data.cdf   set the name of output file (required)"<<std::endl;
  std::cout<<" -minE 20                provide the lower bound of energy cut in % with repect to 511 keV"<<std::endl;
  std::cout<<"                         for example -minE lowCut means a cut of 511.*(1 - lowCut/100.)"<<std::endl;
  std::cout<<" -maxE 60                provide the upper bound of energy cut in % with repect to 511 keV"<<std::endl;
  std::cout<<"                         for example -maxE hiCut means 511(1. + hiCut*/100.)"<<std::endl;
  std::cout<<" -filter                 to filter out angled lines of response"<<std::endl;
  exit(-2);
}
