### phase_1

answer

```
Public speaking is very easy.
1 2 6 24 120 720
7 b 524
9 austinpowers 
/0%+-!
4 2 6 3 1 5 
1001
```

反汇编代码如下

![phase_1_disas](../../Pictures/Blog/lab-work/phase_1_disas.png)

这里的关键函数显然是<strings_not_equal>，在执行<strings_not_equal>时，两个参数入栈，经过实际测试（这里使用了gdb的一个插件pwndbg），一个参数是输入，一个参数是目标字符串，测试过程如下：

我们在输入时尝试输入字符串"11111111"时

![phase_1_input](../../Pictures/Blog/lab-work/phase_1_input.png)

查看下栈信息，可以看到ebx+0x8的内存地址存的数据为0x804b680，根据反汇编代码，这个数据要传给eax,然后作为一个参数入栈，另一个参数是立即数0x80497c0

![phase_1_stack](../../Pictures/Blog/lab-work/phase_1_stack.png)

接下来打印传入的两个参数作为内存地址储存了什么字符串：

![phase_1_args12](../../Pictures/Blog/lab-work/phase_1_args12.png)

可以看到传参确实符合猜测，eax存放输入字符串的内存地址，立即数0x80497c0存放目标字符串的内存地址。

动态调试同时发现strings_not_equal函数通过比较传入字符串和目标字符串，改变eax的数值，相等eax为0,不等为1,也符合`<+28>`,`<+30>`处的判断;

我们已经知道了目标字符串是“Public speaking is very easy.”，尝试传入结果，通过检测。

![lab_work_phase1_result](../../Pictures/Blog/lab-work/lab_work_phase1_result.png)

### phase_2

反汇编代码

![phase_2_disas](../../Pictures/Blog/lab-work/phase_2_disas.png)

注意这里`<+19>`处要读入六个数字，我们确定了字符类型为六个数字，我们这里不妨输入"1 2 3 4 5 6"，执行`<+19>`处

`<read_six_numbers>`后，栈变成了以下模样

![phase_2_stack](../../Pictures/Blog/lab-work/phase_2_stack.png)

很明显`<+27>`处`  cmpl  $1, -0x18(%ebp)`是将立即数1与栈上`%ebp-0x18`地址存放的地址`0xffffcc00`指向内容（第一个数字`1`）比较，我们这里满足，后面的关键就是要过下面这一段的循环

![phase_2_xunhuan](../../Pictures/Blog/lab-work/phase_2_xunhuan.png)

这里关键的地方在与`<+46>`处的相乘操作，这一步实际上实现了`v[i] = v[i-1] * i`的效果，这里eax原本是下标`i`（因为`<+46>`处)，而`-4（%esi,%ebx,4)`实际上对应了上一个数字`v[i-1]`。两个数相乘结果放在eax里，再比较参数`v[i]`是否等于eax。根据参数1为1。我们可以构造`1 2 6 24 120 720`，尝试输入，满足题意。

![lab_work_phase2_result](../../Pictures/Blog/lab-work/lab_work_phase2_result-17011638523391.png)

### phase_3

反汇编代码：

![phase_3_disas1](../../Pictures/Blog/lab-work/phase_3_disas1.png)

![phase_3_disasm2](../../Pictures/Blog/lab-work/phase_3_disasm2.png)

首先看下`sscanf@plt   `的调用，了解到该函数的第一个参数是字符串，第二个参数是格式,同时，该函数返回匹配的参数个数。

```c
int sscanf(const char *str, const char *format, ...)
```

```c
//Example:

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main () {
   int day, year;
   char weekday[20], month[20], dtm[100];

   strcpy( dtm, "Saturday March 25 1989" );
   sscanf( dtm, "%s %s %d  %d", weekday, month, &day, &year );

   printf("%s %d, %d = %s\n", month, day, year, weekday );
    
   return(0);
}

//result
//March 25, 1989 = Saturday
```

我们关心格式，打印下格式

![phase_3_soving](../../Pictures/Blog/lab-work/phase_3_soving.png)

这里可以看到edx保存了输入字符串保存的地址。输入格式是“%d %c %d”,可以看到后面eax需要大于2，也就是说输入需要完全匹配这个格式。再往后会把栈中数据和0x7比较，看下栈上数据即可，动态调试发现这个数据就是输入‘’%d %c %d‘’中的第一个%d,至于为什么这个数据被放栈上了，实际上是在sscanf执行前的参数入栈决定的，这是入栈的参数

![phase_3_sscanf_stack](../../Pictures/Blog/lab-work/phase_3_sscanf_stack.png)

执行sscanf以后

![phase_3_sscanf_after_stack](../../Pictures/Blog/lab-work/phase_3_sscanf_after_stack.png)

![phase_3_stack](../../Pictures/Blog/lab-work/phase_3_stack.png)

可以看到，符合预期，后面的重点放在0xffffcbfc 0xffffcc03 0xffffcc04处即可，容易发现，他们也在栈上，并且，0xffffcbfc处恰好就是要与0x7比较的栈上数据，ja是无符号大于，+240处是炸弹，也就是这里参数一小于等于7,且无符号数。后面，参数1作为偏移量，跳转到0x80497e8加偏移量乘4内存处地址存放的数据指向的指令，看下这个指令在哪个地址（这里以0作为偏移量)。

![phase_3_jmp](../../Pictures/Blog/lab-work/phase_3_jmp.png)

很容易可以看到，这里参数1为0时，要跳转到0x8048be0,这里观察发现其实就是跳转到<+72>的位置

继续往下走

![phase_3_switch](../../Pictures/Blog/lab-work/phase_3_switch.png)

这里0x309和第二个%d比较，0x71ffcb80的低位和0x71比较，这里都是正确的，直接结束程序，进入下一阶段，当然根据偏移量的不同，该题答案不同，其他偏移量的情况大多也与该次情况类似，不多赘述。

![phase_3_ans](../../Pictures/Blog/lab-work/phase_3_ans.png)

经过实验，该题八种不同的答案为

``` 
0 q 777
1 b 214
2 b 755
3 k 251
4 o 160
5 t 458
6 v 780
7 b 524
```

实验结果

![lab_work_phase3_result](../../Pictures/Blog/lab-work/lab_work_phase3_result.png)

### phase_4

反汇编代码如下

![phase_4_disas](../../Pictures/Blog/lab-work/phase_4_disas.png)

sscanf函数重合了，看下格式要求输入数字，大致看了一眼汇编，发现这个数字需要大于0,该数字同时作为参数传入fun4,fun4的返回值要是55（0x37）,所以关键就落在了fun4上

![phase4_fun4_disas](../../Pictures/Blog/lab-work/phase4_fun4_disas.png)

这里0x8(%ebp)位置为上一个栈帧，保存了传入参数9，也就是，当传参小于1时，直接给eax置1,返回。

否则，执行fun(n-1)+fun(n-2),明显是递归，c代码尝试逆向如下

```c
int func4(int n){
if(n <= 1)
    return 1;
else
    return func4(n-1)+func(n-2);
}
```

解密程序

```c
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
```

编译运行，结果为9,尝试输入9,结果正确。实验结果：

![lab_work_phase_4](../../Pictures/Blog/lab-work/lab_work_phase_4.png)

### phase_5

反汇编代码如下：

![phase_5_disas](../../Pictures/Blog/lab-work/phase_5_disas.png)

汇编信息：前面一段保证字符串需要有六个字符，到<+38>处看一眼，打印下0x804b220

![phase_5_xs](../../Pictures/Blog/lab-work/phase_5_xs.png)

容易知道，这段数组的存放地址被放入了esi寄存器，经历五轮循环，依次取出输入字符，取出字符后仅要低四位，作为数组该数组的数组下标取出字符，放入al寄存器以后转移到0xffffcc00，可以看到第一次取出字符‘O’(0x4f)，截取出0xf（15），作为下标，取出arry[15],即字符‘g’，放入0xffffcc00的位置，如此经历循环，直到0xffcc00处有六个字符。

![phase_5_firstrun](../../Pictures/Blog/lab-work/phase_5_firstrun.png)

后面执行strings_not_equal函数，入栈两个参数，一个是0xffffcc00，即-2(%ebp)，也即%ecx，一个是0x804980b，看下0x804980b，发现是字符串“giants”。


![phase_5_dest-str](../../Pictures/Blog/lab-work/phase_5_dest-str.png)

该字符串中字符在开头数组中的下标依次是
```c
0xf 0x0 0x5 0xb 0xd 0x1
```


![phase_5_xs](../../Pictures/Blog/lab-work/phase_5_xs.png)

根据ASCII码表，可知

```c
0xf{'/' '?' 'O' '_' 'o'}
0x0{'0' '@' 'P' '`' 'p'}
0x5{'%' '5' 'E' 'U' 'e' 'u'}
0xb{'+' ';' 'K' '[' 'k' '{'}
0xd{'-' '=' 'M' ']' 'm' '}'}
0x2{'！' '1' 'A' 'Q' 'a' 'q'}
```

从上到下依次在大括号里随机选择一个字符组成字符串即可。

![ascii](../../Pictures/Blog/lab-work/ascii.png)

试验结果

![lab_work_phase5](../../Pictures/Blog/lab-work/lab_work_phase5.png)

### phase_6

反汇编后代码如下

![phase_6_disas1](../../Pictures/Blog/lab-work/phase_6_disas1.png)

![phase_6_disas2](../../Pictures/Blog/lab-work/phase_6_disas2-17018753864231.png)

![phase_6_disas3](../../Pictures/Blog/lab-work/phase_6_disas3-17018754258802.png)

前面代码逻辑比较简单，read_six_numbers函数将尝试输入的字符“1 2 3 4 5 6”放在栈上的特定位置，以便后续使用；并将链表的第一个元素node1(0x804b26c)放栈上；同时，我们打印链表的结构，方便后续使用。

![phase_6_readsixnums](../../Pictures/Blog/lab-work/phase_6_readsixnums.png)

![phase_6_lianbiao](../../Pictures/Blog/lab-work/phase_6_lianbiao-17019573494321.png)

下一阶段是和一个循环一起使用来保证输入的每一个数均小于等于6

![phase_6_everynumgreater6](../../Pictures/Blog/lab-work/phase_6_everynumgreater6.png)

继续向下读，结合上面这段，发现这不但是个循环，还是个双层循环，这段需要仔细读。我会给出C风格的伪代码来方便理解。

![phase_6_2for](../../Pictures/Blog/lab-work/phase_6_2for.png)

这一段的伪代码如下

```c
for(int i = 0;i <= 5;i++){
    if(v[i] > 6)
            explode_bomb();
	for(int j = i+1;j <=5;j++){
        if(v[i] == v[j])
            explode_bomb();
    }
}
```

这段保证了输入的六个数字均小于等于6,且互不相等。

![phase_6_ebx2eax](../../Pictures/Blog/lab-work/phase_6_ebx2eax.png)

应该注意到，这块代码大概分成两个部分，在<+120>前，主要进行了一些栈初始化的操作，以方便接下来的使用。<+120>到<+170>是一个大循环。主要是将链表以输入数字的顺序依次放在栈空间上，核心操作步骤是<+163>,循环结束后形成的栈如下图所示。

![phase_6_lianbiao2stack](../../Pictures/Blog/lab-work/phase_6_lianbiao2stack.png)

后面这段根据栈上链表的顺序，对原链表进行了重新指向设定。

![phase_6_relianbiao](../../Pictures/Blog/lab-work/phase_6_relianbiao.png)

这段循环执行后链表的结构如图所示

![phase_6_relianbiao2](../../Pictures/Blog/lab-work/phase_6_relianbiao2.png)

来看最后一部分

![phase_final_disas](../../Pictures/Blog/lab-work/phase_final_disas.png)

可将其分成3部分。第一部分是<+216>之前的栈/寄存器初始化，第二部分是<+216>至<+237>之间的循环体，第三部分是之后的销毁栈指令。重点在循环体处，在循环中，要求每一个链表后的元素必须小于或等于当前链表中的元素。因此，我们将初始链表进行排序，作为输入参数传入，即可拆弹成功。

![phase_6](../../Pictures/Blog/lab-work/phase_6.png)

### secret_phase

入口寻找比较简单，注意到每次通过一个phase,都会经过一个phase_defused函数，反汇编看下，这个函数是干嘛的。

![phase_defuse_disas](../../Pictures/Blog/lab-work/phase_defuse_disas.png)

<+7>处的比较要求0x804b480处的值与0x6相等。下面是通过第一阶段以后的0x804b480,经过尝试，每通过一个阶段，储存在该位置的数据加一，此处相当于记录了通过的关数，因此，只有走第六关以后的那个phase_defused函数才能进入secret_phase。实际上，incl num_input_strings在每个阶段执行前的<read_line+180>处执行，因此，每到一关，0x804b480处的数值加一。

![de_num](../../Pictures/Blog/lab-work/de_num.png)

再往下走发现熟悉的sscanf函数，看下传入参数

![phase_defused](../../Pictures/Blog/lab-work/phase_defused.png)

应该注意到，这里的“9 ”是第四关输入数据，检测的格式是“%d %s”,这是否提示我们：第四关的输入不止有“9”，还有一个字符串？继续向下看，要求sscanf返回值为2,也就是我们必须再输入一个字符串。注意到下面还有strings_not_equal函数，我们查看该函数的入栈参数，判断需要输入字符串的具体情况。

![defused2secret](../../Pictures/Blog/lab-work/defused2secret.png)

所以，我们在第四行“9”后面输入“austinpowers”,开启secret_phase函数。看下secret_phase函数的反汇编代码

![secret_phase_disas](../../Pictures/Blog/lab-work/secret_phase_disas.png)

汇编的逻辑并不复杂，把输入字符串转成长整型之后，该长整型数据大小必须小于或等于1001,并与n1一起传入函数fun7,要求函数fun7的返回值为7。我们重点关注fun7实现的功能。

fun7的反汇编如下

![fun7_disas](../../Pictures/Blog/lab-work/fun7_disas.png)

可知道，该函数实现了对二叉树的操作，先打印下传入的二叉树。我们从传入fun7的n1参数，即根节点0x804b320开始打印该二叉树。

![2chaTree](../../Pictures/Blog/lab-work/2chaTree.png)

我们可以把这棵树画出来

```c
         36
    8          50
 6    22    45    107
1 7 20 35 40 47 99 1001           
```

这个阶段的汇编并不复杂，主要是根据传入数据和当前节点递归处理来寻找目标二叉树节点，并对返回值进行处理。传入数据如果大于该节点储存的值，向左寻找，向左寻找会将被递归的fun7的返回值n进行（n`*`2+1）的处理；传入数据如果小于储存的值，向右寻找，向右边寻找会将被递归的fun7的返回值n进行(n`*`2)的处理；如果传入数据等于当前节点，直接返回0。因此只能一直向右左边边寻找得到1001，倘若在107-1001之间，<+14>处不会跳转，eax会变0xffffff,也不满足题目意思，因此，只能找到1001节点本身。自然，答案是1001。我们最后来验证一下成果：

![answer](../../Pictures/Blog/lab-work/answer.png)

可以看到所有阶段，包括secret stage阶段，都已经被攻克。
