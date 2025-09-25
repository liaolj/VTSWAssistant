# 兼容矩阵与插入策略

| 场景 | 首选 | 备选 | 兜底 | 备注 |
|---|---|---|---|---|
| 浏览器 input/textarea | SendInput | UIA | 剪贴板 | 光标稳定性较好 |
| Gmail 富文本（网页） | SendInput | 剪贴板 | — | 选择纯文本粘贴 |
| Notion 桌面 | SendInput | UIA | 剪贴板 | 某些块需先激活 |
| Jira（网页） | SendInput | 剪贴板 | — | 描述区支持粘贴列表 |
| Slack/飞书/微信 PC | SendInput | UIA | 剪贴板 | @ 人名建议手动 |
| Word/Outlook/WPS | UIA | SendInput | 剪贴板 | 保留格式，注意撤销栈 |
| VSCode/记事本 | SendInput | — | 剪贴板 | 代码块按段落插入 |

**撤销粒度**：最近一次插入块；大块分批（>1200 字）以避免卡顿。  
**焦点保护**：插入前后比对窗口句柄，若变化则提示用户复位光标。
