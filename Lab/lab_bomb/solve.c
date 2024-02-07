#include <stdio.h>

int func4(int n){
    if(n <= 1)
        return 1;
    else
        return func4(n-1)+func4(n-2);
}

int main(){
    int result = 55; // 该函数的返回值
    int n = 0;
    while(func4(n) != result){
        n++;
    }
    printf("该函数的传入值为：%d\n", n);
    return 0;
}
