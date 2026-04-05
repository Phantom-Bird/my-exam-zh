> [!INFO]
> 仅在原版宏包上略加改动，用法参照原版宏包。

改动内容：
1. 加入了 `\tpi`，使用 Times New Roman 的 π 来代替 `unicode-math` 看起来不正的正体 π；
2. 支持修改“绝密 ★ 启用前”以防止法律风险。
   ```tex
   \secret[\makesecret{等级}{时间}]
   ```
   也可以在右侧添加试卷类型：
   ```tex
   \secret[\makesecret{等级}{时间} \hfill \Large{\heiti {试卷类型: A}}]
   ```
3. 将 `\notice` 间距减少了 `2pt`，可以通过以下方法回调：
   ```tex
   \begin{notice}[][itemsep=0pt]
       \item ...
       \item ...
   \end{notice}
   ```
