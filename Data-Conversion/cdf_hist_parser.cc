/*
Program to parse and display castor histogram file


Last edited Apr 24, 2020

// Title            :   cdf_hist_parser.cc
// Date             :   April, 24 2020
// Author           :   J Nsofini
// Version          :   1.1
// Description      :   passing castor-recon histogram cdf data
// Last Edit        : 
// Options          : 

last edits:
Added: 

Features of the program:
reads th bin cdf file and print to consol
*/



#include <fstream>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

std::string inname = "";

void Usage(void);
void ParseCommandLineArguments(int narg, char* argv[]);
int ReadCASTORdata(std::fstream *fs);

int main(int narg, char* argv[])
{
    ParseCommandLineArguments(narg, argv);

    std::fstream inFile;
    inFile.open(inname, std::ios::in | std::ios::binary);

    int counter=0;
    int counter_val = 1500625;
    
    if(!inFile.is_open())  std::cerr<<"could not open "<<inname<<" "<<__FILE__<<" "<<__LINE__<<std::endl;


    while(inFile.good() and counter <1000){
	  ReadCASTORdata(&inFile);
	  ++counter;
	} 

    
  inFile.close();
  std::cout<<"Counts: "<<counter <<std::endl;
  return 0;
}


int ReadCASTORdata(std::fstream *fs)
{


    //unsigned int t =0;                          //time in ms
    //fs->read((char *)&t, sizeof(unsigned int));
    //std::cout<<"time = "<<t<<": ";
    // float a = 0;                                //Attenuation correction factor *optional*
    // fs->read((char *)&a, sizeof(float));        
    // float s = 0;                                //Un-normalized scatter intensity rate of the 
    // fs->read((char *)&s, sizeof(float));        //corresponding event (count/s) *optional*
    // float r = 0;                                //Un-normalized random intensity rate of the 
    // fs->read((char *)&r, sizeof(float));        //corresponding event (count/s) *optional*
    // float n = 0;                                //Normalization factor of the corresponding 
    // fs->read((char *)&n, sizeof(float));        //event  *optional*
    // short k= 0;                                 //Number of contributing crystal pairs
    // fs->read((char *)&k, sizeof(short));        //Mandtory if k>1

    if(fs->eof())return -1;
  
    // std::cout<<"t = "<<t<<": a = "<<a<<": s = "<<s<<": r = "<<r<<": n = "<<n
    // 	   <<": k = "<<k<<std::endl;
    int castorID1 = 0;
    int castorID2 = 0;
    unsigned int t = 0;    
    float scat_coef = 0.0;
    // for(int i =0; i<k; i++)
    //    {
 
        fs->read((char *)&t, sizeof(unsigned int));
        fs->read((char *)&scat_coef, sizeof(float));
        fs->read((char *)&castorID1, sizeof(int));
        fs->read((char *)&castorID2, sizeof(int));
        //norm[castorID1][castorID2] = normCoef;
        //norm_vec[castorID1][castorID2] = normCoef;

        std::cout<<"CastorID1 = "<<castorID1<<": CastorID2 = "<<castorID2 
        <<": Scattering Coef = "<<scat_coef <<": Binning time = "<<scat_coef   <<std::endl;
        //std::cout<<"From array: castorID1 = "<<castorID1<<": castorID2 = "<<castorID2 <<": normCoef = "<< norm_vec[castorID1][castorID2]  <<std::endl;
        //     }

  // for(int i=0; i<1-k; i++)
  //   {
  //     unsigned int garbage1 =0;
  //     fs->read((char *)&garbage1, sizeof(unsigned int));
  //     unsigned int garbage2 =0;
  //     fs->read((char *)&garbage2, sizeof(unsigned int));

  //     std::cout<<": garbage1 = "<<garbage1
  // 	       <<": garbage2 = "<<garbage2<<std::endl;
  //   }
  return 0;
}



//----------------------------
// ParseCommandLineArguments
//----------------------------
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
    }

  if(inname=="")
    {
      Usage();
    }

  std::cout<<" Input file name = "<<inname<<std::endl;
}


//----------------------------
// Usage
//----------------------------
void Usage(void)
{
  std::cout<<std::endl;
  std::cout<<"Usage:"<<std::endl;
  std::cout<<"      exec_name: -inF CASTOR_data.cdf"<<std::endl;
  std::cout<<std::endl;
  std::cout<<"  options:"<<std::endl;
  std::cout<<" -h                      print this help message"<<std::endl;
  std::cout<<" -inF CASTOR_data.cdf set the name of MC data file (required)"<<std::endl;
  exit(-2);
}
