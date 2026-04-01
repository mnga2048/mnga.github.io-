# BLDC控制方式：PWM vs 简单通断

## 一、核心答案

### ✅ **可以不用PWM！但有限制**

| 控制方式 | 能转动吗？ | 能调速吗？ | 应用场景 |
|---------|-----------|-----------|---------|
| **PWM控制** | ✅ 能 | ✅ 能 | 精确调速、平稳运行 |
| **简单通断** | ✅ 能 | ❌ 不能 | 简单启动、定速运行 |

---

## 二、两种控制方式详解

### 2.1 PWM控制（推荐）

#### **工作原理：**
```
PWM = 脉冲宽度调制

通过改变占空比来控制电压有效值：
┌─────┐   ┌─────┐   ┌─────┐
│     │   │     │   │     │
└─────┘   └─────┘   └─────┘
 50%占空比 → 50%电压 → 50%转速

┌──┐  ┌──┐  ┌──┐  ┌──┐
│  │  │  │  │  │  │  │  │
└──┘  └──┘  └──┘  └──┘
 25%占空比 → 25%电压 → 25%转速
```

#### **代码示例：**
```c
// 方式1：可调速
PWM_SetDuty(UH, 500);  // 50%占空比，中等转速
PWM_SetDuty(UH, 800);  // 80%占空比，高速
PWM_SetDuty(UH, 200);  // 20%占空比，低速

// 方式2：定速但更平稳
PWM_SetDuty(UH, 600);  // 固定60%，但比纯通断平稳
```

#### **优点：**
- ✅ 转速可调
- ✅ 转矩平稳
- ✅ 效率高
- ✅ 噪音小
- ✅ 启动电流小

#### **缺点：**
- ❌ 代码复杂
- ❌ 需要定时器资源
- ❌ 调试困难

---

### 2.2 简单通断控制（你能想到的方式）

#### **工作原理：**
```
简单通断 = 只有全开和全关两种状态

换相时：
┌────────────────────────────┐
│   PWM输出100%占空比        │
│   (实际上是持续输出高电平)  │
└────────────────────────────┘

例如：A相通电
A相上臂(MOSFET) = 一直导通
B相下臂(MOSFET) = 一直导通
结果：A相一直通100%电压
```

#### **代码示例：**
```c
// 简单通断实现
void Simple_Commutation(uint8_t hall)
{
    // 先关闭所有桥臂
    GPIO_ResetBits(GPIOA, UH | UL | VH | VL | WH | WL);

    // 根据霍尔状态导通对应桥臂
    switch(hall)
    {
        case 0x06:  // Step 1: A-B
            GPIO_SetBits(GPIOA, UH);   // A相上臂导通
            GPIO_SetBits(GPIOA, VL);   // B相下臂导通
            // 注意：这里没有PWM，就是100%占空比
            break;

        case 0x04:  // Step 2: A-C
            GPIO_SetBits(GPIOA, UH);
            GPIO_SetBits(GPIOA, WL);
            break;

        // ... 其他状态
    }
}

// 或者用固定PWM（100%占空比）
void FixedPWM_Commutation(uint8_t hall)
{
    MCPWM_SetDuty(UH, 1000);  // 100%占空比 = 等效于直通
    MCPWM_SetDuty(VL, 1000);
    // 但这样本质上还是PWM，只是占空比固定
}
```

#### **优点：**
- ✅ 代码非常简单
- ✅ 容易理解
- ✅ 调试方便
- ✅ 不需要复杂的定时器

#### **缺点：**
- ❌ **无法调速**（只能全速运行）
- ❌ 启动电流大
- ❌ 转矩脉动大
- ❌ 噪音大
- ❌ 效率低

---

## 三、为什么简单通断也能转动？

### 3.1 原理分析

```
BLDC电机转动的关键：
1. 正确的换相时机（霍尔状态）
2. 定子磁场方向
3. 转子磁场跟随

只要满足这3个条件，电机就会转动！

PWM vs 简单通断的区别：
┌─────────────────────────────────────┐
│ PWM控制：                           │
│ - 换相时机 ✓                       │
│ - 磁场方向 ✓                       │
│ - 转子跟随 ✓                       │
│ - 电压大小可调（通过占空比）      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 简单通断：                          │
│ - 换相时机 ✓                       │
│ - 磁场方向 ✓                       │
│ - 转子跟随 ✓                       │
│ - 电压大小固定（100%）            │
└─────────────────────────────────────┘

结论：都能转动！只是调速方式不同
```

---

### 3.2 电压与转速关系

```
理想情况：
转速 ∝ 电压

实际情况：
转速 = 电压 × K - 负载转矩

简单通断：
电压 = 100% → 转速 = 100% - 负载影响
       = 固定转速（实际上会随负载变化）

PWM控制：
电压 = 50% → 转速 = 50% - 负载影响
       = 可调转速
```

---

## 四、三种实现方式对比

### 方式1：纯GPIO通断（最简单）

```c
void Commutation_GPIO_Style(uint8_t hall)
{
    // 全部关闭
    TURN_OFF_ALL();

    // 根据霍尔状态导通
    switch(hall)
    {
        case 0x06:  // A-B
            GPIO_WriteBit(UH, 1);  // 导通
            GPIO_WriteBit(UL, 0);
            GPIO_WriteBit(VH, 0);
            GPIO_WriteBit(VL, 1);  // 导通
            GPIO_WriteBit(WH, 0);
            GPIO_WriteBit(WL, 0);
            break;
        // ... 其他状态
    }
}
```

**特点：**
- 😊 **最简单**，直接GPIO控制
- 😊 **代码量少**，<50行
- 😊 **容易调试**，直接看IO状态
- 😡 **启动电流大**，可能烧MOSFET
- 😡 **无法调速**，只能全速
- 😡 **噪音大**，震动大

**适用场景：**
- ✅ 学习BLDC原理
- ✅ 验证硬件连接
- ✅ 简单的演示程序

---

### 方式2：固定占空比PWM（折中）

```c
void Commutation_FixedPWM_Style(uint8_t hall)
{
    uint16_t duty = 600;  // 固定60%

    MCPWM_SetDuty(UH, duty);  // 虽然是PWM，但占空比固定
    MCPWM_SetDuty(VL, duty);
    // 换相时改变通道，但占空比不变
}

void Switch_Phase(uint8_t hall)
{
    MCPWM_Cmd(ALL_CHANNELS, DISABLE);  // 先关闭
    Delay_us(50);  // 死区时间

    switch(hall) {
        case 0x06:
            MCPWM_SetChannel(UH, 600);
            MCPWM_SetChannel(VL, 600);
            MCPWM_Cmd(UH | VL, ENABLE);
            break;
        // ...
    }
}
```

**特点：**
- 😊 **比较简单**，占空比固定
- 😊 **启动电流小一些**，有死区控制
- 😊 **噪音小一点**，比纯通断平滑
- 😡 **还是无法调速**
- 😡 **占空比固定**，效率一般

**适用场景：**
- ✅ 定速运行（如风扇）
- ✅ 对转速要求不高
- ✅ 想要简单但有死区保护

---

### 方式3：可变占空比PWM（完整）

```c
uint16_t current_duty = 0;

void Commutation_VariablePWM_Style(uint8_t hall)
{
    MCPWM_Cmd(ALL_CHANNELS, DISABLE);
    Delay_us(50);

    switch(hall) {
        case 0x06:
            MCPWM_SetDuty(UH, current_duty);  // 占空比可调
            MCPWM_SetDuty(VL, current_duty);
            MCPWM_Cmd(UH | VL, ENABLE);
            break;
        // ...
    }
}

// 主循环调节转速
int main(void)
{
    current_duty = 300;  // 30% → 低速
    // ...
    current_duty = 800;  // 80% → 高速
}
```

**特点：**
- 😊 **转速可调**，范围大
- 😊 **启动平稳**，软启动
- 😊 **效率高**，噪音小
- 😡 **代码复杂**
- 😡 **需要PID闭环**

**适用场景：**
- ✅ 需要精确调速
- ✅ 需要稳定运行
- ✅ 商业产品

---

## 五、实际应用建议

### 5.1 根据需求选择

```
需求分析：
┌─────────────────────────────────┐
│ 只是想让它转？                  │ → 纯GPIO通断
│ 验证硬件和换相逻辑？            │
├─────────────────────────────────┤
│ 需要稳定运行，但转速固定？      │ → 固定PWM
│ 如：散热风扇、水泵              │
├─────────────────────────────────┤
│ 需要调速功能？                  │ → 可变PWM
│ 如：无人机、电动车、精密设备    │
└─────────────────────────────────┘
```

---

### 5.2 渐进式开发路线

```
第1阶段：验证原理（1天）
├─ 使用纯GPIO通断
├─ 验证换相逻辑是否正确
└─ 验证电机能否转动

第2阶段：改进控制（2-3天）
├─ 使用固定PWM（60%）
├─ 添加死区控制
└─ 观察运行效果

第3阶段：闭环控制（1-2周）
├─ 添加转速测量
├─ 实现可变PWM
├─ 添加PID控制
└─ 完整调速功能
```

---

## 六、关键技术点

### 6.1 死区时间（重要！）

```
为什么需要死区？

MOSFET不能瞬间切换：
上臂关断 ─┐
           ├─ 必须有时间间隔（死区）
下臂导通 ─┘

如果没有死区：
→ 上下臂同时导通
→ 电源短路！
→ 烧MOSFET！

纯GPIO方式的问题：
GPIO输出切换很快，但没有硬件死区保护
→ 容易短路

PWM方式的优势：
MCPWM模块有硬件死区保护
→ 安全
```

---

### 6.2 启动电流

```
纯GPIO通断启动：
┌───────────┐
│ 100%电压 │ → 启动电流可能是额定电流的5-10倍
└───────────┘

PWM软启动：
┌────┐┌────┐┌────┐
│30% │→50% │→80% │ → 逐步增加，电流小
└────┘└────┘└────┘

结论：PWM启动更安全
```

---

### 6.3 换相时机

```
无论哪种方式，换相时机都是一样的！

纯GPIO：
检测到霍尔变化 → GPIO切换桥臂

固定PWM：
检测到霍尔变化 → PWM切换通道（占空比不变）

可变PWM：
检测到霍尔变化 → PWM切换通道 + 调整占空比

关键：换相逻辑相同，只是输出方式不同
```

---

## 七、代码对比

### 7.1 纯GPIO方式（最简单）

```c
// 完整代码 < 100行
void main(void)
{
    GPIO_Init();
    uint8_t hall_old = 0, hall_new = 0;

    while(1)
    {
        hall_new = Read_Hall();

        if(hall_new != hall_old)
        {
            Simple_Commutation(hall_new);
            hall_old = hall_new;
        }

        Delay_us(100);
    }
}

void Simple_Commutation(uint8_t hall)
{
    // 全部关闭
    GPIOA->ODR &= ~(UH|UL|VH|VL|WH|WL);

    switch(hall)
    {
        case 0x06: GPIOA->ODR |= UH|VL; break;
        case 0x04: GPIOA->ODR |= UH|WL; break;
        case 0x05: GPIOA->ODR |= VH|WL; break;
        case 0x01: GPIOA->ODR |= VH|UL; break;
        case 0x03: GPIOA->ODR |= WH|UL; break;
        case 0x02: GPIOA->ODR |= WH|VL; break;
    }
}
```

---

### 7.2 可变PWM方式（完整）

```c
// 完整代码 > 300行
volatile uint16_t duty = 0;
volatile uint16_t target_rpm = 0;
volatile uint16_t actual_rpm = 0;

int main(void)
{
    SystemInit();
    MCPWM_Init();
    Timer_Init();
    PID_Init();

    target_rpm = 1000;

    while(1)
    {
        // PID控制
        int16_t error = target_rpm - actual_rpm;
        duty += PID_Calculate(error);

        // 限幅
        if(duty > 1000) duty = 1000;
        if(duty < 0) duty = 0;

        Delay_ms(10);
    }
}

void TIM0_IRQHandler(void)
{
    uint8_t hall = Read_Hall();
    PWM_Commutation(hall, duty);
    Calculate_Speed();
}

void PWM_Commutation(uint8_t hall, uint16_t duty)
{
    static uint8_t hall_old = 0;

    if(hall != hall_old)
    {
        MCPWM_Cmd(ALL, DISABLE);
        Delay_us(50);  // 死区

        switch(hall)
        {
            case 0x06:
                MCPWM_SetDuty(UH, duty);
                MCPWM_SetDuty(VL, duty);
                MCPWM_Cmd(UH|VL, ENABLE);
                break;
            // ...
        }

        hall_old = hall;
    }
}
```

---

## 八、性能对比

### 8.1 转速稳定性

```
纯GPIO通断：
转速 = 100% ± 20%（随负载波动大）

固定PWM：
转速 = 100% ± 10%（平稳一些）

可变PWM：
转速 = 设定值 ± 2%（非常稳定）
```

---

### 8.2 电流波形

```
纯GPIO通断：
电流 ┌───┐  ┌───┐  ┌───┐
     │   │  │   │  │   │  脉动大
     └───┘  └───┘  └───┘

可变PWM：
电流 ─────────────────────  平滑
     ─────────────────────
```

---

### 8.3 噪音水平

```
纯GPIO通断：
噪音 = 80-100 dB（很吵）

固定PWM：
噪音 = 60-70 dB（一般）

可变PWM：
噪音 = 40-50 dB（较安静）
```

---

## 九、实际项目建议

### 9.1 推荐方案

```
学习阶段：
└─ 纯GPIO通断（快速验证原理）

原型验证：
└─ 固定PWM（60%，有死区保护）

产品开发：
└─ 可变PWM + PID（完整功能）
```

---

### 9.2 你的项目建议

**单片机具有MCPWM模块 → 强烈建议用PWM！**

**理由：**
1. 硬件支持，不用白不用
2. MCPWM有死区保护，更安全
3. 代码复杂度增加不多
4. 性能提升巨大

**折中方案：**
```
第1版：固定PWM（60%占空比）
├─ 代码简单
├─ 比纯通断安全
└─ 满足基本运行

第2版：可变PWM
├─ 添加调速功能
├─ 添加转速测量
└─ 添加PID控制
```

---

## 十、总结

### 核心结论

| 问题 | 答案 |
|------|------|
| **不用PWM能转吗？** | ✅ 能！ |
| **能调速吗？** | ❌ 不能（只能全速） |
| **推荐用PWM吗？** | ✅ 强烈推荐！ |
| **纯GPIO有什么用？** | 验证原理、学习 |

### 最佳实践

```
开发顺序：
1. 先用纯GPIO验证换相逻辑（1天）
2. 改用固定PWM（2-3天）
3. 最后升级到可变PWM（1-2周）

这样既能快速验证，又能保证最终质量
```

### 你的选择

**建议：**
- ✅ **学习阶段**：纯GPIO通断（快速理解）
- ✅ **实际应用**：固定PWM（60%）或可变PWM
- ❌ **不推荐**：产品中用纯GPIO通断

---

## 附录：完整代码示例

### 纯GPIO通断（完整可运行）

```c
#include "w32f006.h"

#define UH  GPIO_Pin_0
#define UL  GPIO_Pin_1
#define VH  GPIO_Pin_2
#define VL  GPIO_Pin_3
#define WH  GPIO_Pin_4
#define WL  GPIO_Pin_5

void GPIO_Init_BLDC(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;

    RCC_APBPeriphClockCmd(RCC_AHBCLKCTRL_GPIO2, ENABLE);

    // 配置6个输出口（推挽输出）
    GPIO_InitStruct.GPIO_Pin = UH | UL | VH | VL | WH | WL;
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_Level_2;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIO2, &GPIO_InitStruct);
}

void Commutation_Simple(uint8_t hall)
{
    // 全部关闭
    GPIO2->BRR = UH | UL | VH | VL | WH | WL;

    // 根据霍尔状态导通
    switch(hall)
    {
        case 0x06:  // A-B
            GPIO2->BSRR = UH | VL;
            break;
        case 0x04:  // A-C
            GPIO2->BSRR = UH | WL;
            break;
        case 0x05:  // B-C
            GPIO2->BSRR = VH | WL;
            break;
        case 0x01:  // B-A
            GPIO2->BSRR = VH | UL;
            break;
        case 0x03:  // C-A
            GPIO2->BSRR = WH | UL;
            break;
        case 0x02:  // C-B
            GPIO2->BSRR = WH | VL;
            break;
    }
}

int main(void)
{
    SystemInit();
    GPIO_Init_BLDC();

    uint8_t hall_old = 0;

    while(1)
    {
        uint8_t hall_new = Read_Hall();  // 需要实现这个函数

        if(hall_new != hall_old)
        {
            Commutation_Simple(hall_new);
            hall_old = hall_new;
        }

        Delay_us(100);
    }
}
```

**这就是最简单的BLDC驱动！只有100行代码！**
