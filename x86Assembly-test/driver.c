#include "cdecl.h"

int PRE_CDECL addition( void ) POST_CDECL;

int main()
{
    int ret_status;
    ret_status = addition();
    return ret_status;
}