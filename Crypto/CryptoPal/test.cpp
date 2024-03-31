#include <windows.h>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PSTR pszCmdLine, int nCmdShow)
{
    MessageBox(NULL, TEXT("Hello Windows!"), TEXT("WindowsSDK"), MB_OK);
    return 0;
}