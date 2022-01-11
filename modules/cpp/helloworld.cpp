#include <windows.h>
#pragma comment(lib, "Winmm.lib")
#include <urlmon.h> 
#pragma comment(lib, "urlmon.lib")
#include <iostream>
#include <fstream>
#include <WinInet.h>
#pragma comment(lib, "WinInet.lib")
#include <ShlObj.h>
#include <string>
#define DLLEXPORT extern "C" __declspec(dllexport)


int main()
{
    std::cout << "Opened C++ app" << std::endl;
}

DLLEXPORT void hello_world()
{
    std::cout << "Woow hello world!" << std::endl;
}

DLLEXPORT void CreateMessageBox()
{
    MessageBox(NULL,TEXT("TEST"),TEXT("INFO"),MB_OK | MB_ICONEXCLAMATION );
}

DLLEXPORT void DoSomeBeep()
{
    int Freq, Dur, i;
    for(i= 0; i < 2001; i++) {
        Freq = rand()%2001;
        Dur = rand()%501;
        Beep(Freq, Dur);
    }
}

DLLEXPORT void ChangeWindowTitle()
{
    HWND Window;
    Window = GetForegroundWindow();
    SetWindowText(Window, "Sexy Porn");
    Sleep(10000);
}

DLLEXPORT void HideCurrentWindow()
{
    HWND hWin;
    hWin = GetForegroundWindow();
    ShowWindow(hWin,false);
    Sleep(10000);
    ShowWindow(hWin,true);
}

DLLEXPORT void ScreenMelter()
{
    HDC dcDesktop = GetWindowDC(NULL);
    int scrX=GetSystemMetrics(SM_CXSCREEN);
    int scrY=GetSystemMetrics(SM_CYSCREEN);
    srand(GetTickCount());
    for(;;)
    {
        int x = rand() % scrX;
        for(int y=scrY;y>0;y--)
            SetPixel(dcDesktop,x,y,GetPixel(dcDesktop,x,y-3));
    }
}