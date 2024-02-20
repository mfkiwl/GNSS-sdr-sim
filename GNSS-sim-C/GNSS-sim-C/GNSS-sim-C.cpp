// GNSS-sim-C.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>

#include "ChainLink.h"
#include "DataFrame.h"
#include "Manager.h"
#include "FileSource.h"
#include "FileSink.h"

#include "DataHandler.h"
#include "Resample.h"
#include "IRNSS/PRN_Code.h"

#include "FPGA_data.h"

void example_manager_galileo() {
    //FileSource fileSource("ExampleData.txt");
    //FileSource fileSource("GalileoData.txt");
    FileSource fileSource("../../data/galileo.txt");
    FileSink fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(15000000, 1575420000);

    manager.run(fileSource, fileSink, 1);
}

void example_manager_gps() {
    FileSource fileSource("../../data/gps.txt");
    FileSink fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(2600000, 1575420000);

    manager.run(fileSource, fileSink, 1);
}

void example_manager_gps10() {
    FileSource fileSource("../../data/gps.txt");
    FileSink fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(10000000, 1575420000);

    manager.run(fileSource, fileSink, 1);
}

void example_manager_glonass() {
    //FileSource fileSource("ExampleData.txt");
    FileSource fileSource("../../data/glonass.txt");
    FileSink fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(15000000, 1602000000);

    manager.run(fileSource, fileSink, 1);
}

void example_manager_beidou() {
    FileSource fileSource("../../data/beidou.txt");
    FileSink fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(4000000, 1561098000);

    manager.run(fileSource, fileSink, 1);
}

void example_manager_irnss() {
    FileSource fileSource("../../data/irnss.txt");
    FileSink fileSink("../../data/OutputIQ.sigmf-data");
    Manager manager(2600000, 1176450000);

    manager.run(fileSource, fileSink, 1);
}


void example_chain() {

    galileo::Sat sat(2);

    DataFrame f1;
    f1.delay = 0.00;
    f1.doppler = 0;
    f1.power = 1;
    f1.bits = 0b111110000011111000001111101010;


    DataFrame f2;
    f2.delay = 0.01;
    f2.doppler = 20;
    f2.power = 1;
    f2.bits = 0b000001111100000111110101010101;

    DataHandler* dataHandler = setupChain(&sat, 20000000, 1575420000);

    dataHandler->addFrame(f1);
    dataHandler->addFrame(f2);

    dataHandler->init();

    for (int i = 0; i < 1000; i++) {
        IQ iq = dataHandler->nextSample();
        std::cout << iq << std::endl;
    }

    deleteChain(dataHandler);
}

int main()
{
    std::cout << "Hello World!\n";

    /*irnss::PRN ca (1);
    for (int i = 0; i < 1023; i++) {
        std::cout << (int)ca.next();
    }*/
    generateFPGA_data("../../data/glonass.txt", 1602000000, 15000000, 100);

    //example_manager_glonass();
    //example_manager_galileo();
    //example_manager_gps();
    //example_manager_beidou();
    //example_manager_irnss();
    //example_file();
    //example_chain();
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
