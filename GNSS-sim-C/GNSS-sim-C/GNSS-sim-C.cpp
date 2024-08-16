#include <iostream>
//#include <boost/program_options.hpp>

/* 
    Settings: comment or uncomment #defines to enable options
*/

//#define USE_CBOC              // use CBOC or SinBOC for Galileo Modulation
#define SET_DELAY_ON_START      // set the initial delay when first starting or let it accumilate during the first frame
//#define RELATIVE_MOVE         // enable checks and implementation to allow for quicker updates to the simulated position, resample.[dxmm, dymm, dzmm] have to be set menualy, no nice interface for them
//#define TRIG_LOOKUP           // use a lookup table for trig function, small optimization, little impact on performance
#define IQ_FLOATS               // use floats or int8_t in IQ samples, used in program, but not the output 




#include "DataHandler.h"
//#include "Resample2.h"

#include "ChainLink.h"
#include "DataFrame.h"
#include "Manager.h"
#include "FileSource.h"
#include "FileSink.h"

#include "Server.h"

#include "GPS/PRN_Code.h"

#include "FPGA_data.h"

// these example mangers setup the program for diffrent signals, they are used when loading from a file, and not over the network

void example_manager_config(std::string file) {
    FileSource fileSource(file);
    
    int frequency = 0;
    int samplingRate = 0;
    std::string outputFile;

    if (fileSource.getConfig(&samplingRate, &frequency, &outputFile)) {
        FileSink<int8_t> fileSink(outputFile);
        Manager manager(samplingRate, frequency);
        manager.run_paralell(fileSource, fileSink, 4);
    }
    else {
        std::cerr << "No configuration data found in file: " << file << std::endl;
    }
}

void example_manager_galileo() {

    //FileSource fileSource("ExampleData.txt");
    //FileSource fileSource("GalileoData.txt");
    FileSource fileSource("../../data/galileo.txt");
    FileSink<int8_t> fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(15000000/*2 * 6138000*/, 1575420000);

    manager.run_paralell(fileSource, fileSink, 5);
}

void example_manager_gps() {
    FileSource fileSource("../../data/gps.txt");
    FileSink<int8_t> fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(2600000/*1023000*/, 1575420000);

    //manager.setNoise(-2);
    manager.run_paralell(fileSource, fileSink, 3);
}

void example_manager_gps15() {
    FileSource fileSource("../../data/gps.txt");
    FileSink<int8_t> fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(15000000, 1575420000);

    manager.run(fileSource, fileSink, 1);
}

void example_manager_glonass() {
    //FileSource fileSource("ExampleData.txt");
    FileSource fileSource("../../data/glonass.txt");
    FileSink<int8_t> fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(15000000/*511000*/, 1602000000);

    manager.run_paralell(fileSource, fileSink, 5);
}

void example_manager_beidou() {
    FileSource fileSource("../../data/beidou.txt");
    FileSink<int8_t> fileSink("../../data/OutputIQ_c.sigmf-data");
    Manager manager(/*4000000*/2046000, 1561098000);

    manager.run(fileSource, fileSink, 0);
}

void example_manager_irnss() {
    FileSource fileSource("../../data/irnss.txt");
    FileSink<int8_t> fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(2600000/*1023000*/, 1176450000);

    manager.run(fileSource, fileSink, 0);
}


int main(int argc, char**argv)
{
    // I had problems with boost::program_options so the code is commented out
    /*namespace po = boost::program_options;

    po::options_description desc("Allowed options");
    desc.add_options()
        ("help", "Produce help message")
        ("server", "Alows for making signal generation requests over the network")
        ("file", po::value<std::string>(), "Generate based on a file that includes configuration")
        ("gps", "use default configuration for gps")
        ("galileo", "use default configuration for galileo")
        ("glonass", "use default configuration for glonass")
        ("beidou", "use default configuration for beidou")
        ("irnss", "use default configuration for irnss")
    ;

    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);

    if      (vm.count("help"))    { std::cout << desc << "\n"; }
    else if (vm.count("server"))  { startServer(); }
    else if (vm.count("file"))    { example_manager_config(vm["file"].as<std::string>()); }
    else if (vm.count("gps"))     { example_manager_gps();     }
    else if (vm.count("galileo")) { example_manager_galileo(); }
    else if (vm.count("glonass")) { example_manager_glonass(); }
    else if (vm.count("beidou"))  { example_manager_beidou();  }
    else if (vm.count("irnss"))   { example_manager_irnss();   }
    else {
        std::cout << "No arguments found\n";
    }
    */

    // generate vhdl code for testing that implementation
    //generateFPGA_data("../../data/glonass.txt", 1602000000, 15000000, 100);

    // start a server that waits for a connection to generate and output a signal
    startServer();

    // load intermediate data from a file to generate and output a signal
    //example_manager_config("../../data/gps.txt");
    //example_manager_glonass();
    //example_manager_galileo();
    //example_manager_gps();
    //example_manager_beidou();
    //example_manager_irnss();
}

