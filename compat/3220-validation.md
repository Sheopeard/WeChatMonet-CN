# CN 3220 / 8.0.80 验证记录

日期：2026-11-15（Asia/Shanghai）

## 输入与渠道

- 目标安装包来源：微信官网 `https://weixin.qq.com/`（页面 `__NUXT_DATA__.downloadConf.android`）
- 下载地址：`https://dldir1v6.qq.com/weixin/android/weixin8080android3220_0x28005032_arm64.apk`
- 包名：`com.tencent.mm`
- 版本：`versionName=8.0.80`，`versionCode=3220`（ARM64 正式版）
- 构建标签：`Android_Wechat_RELEASE_WUKONG #8724`（分支 `release/patch/android_2026-t10-8-0-80_2026_10_19_17_20_1@git`，构建时间 `2026-10-30 21:05:21`）
- 目标 APK SHA256：`9d9b6c516e8e07e437c81485fde21fe13ce4f61b37d19e793fff40c71be39c0e`
- 微信签名证书：DN `CN=Tencent, OU=Tencent Guangzhou Research and Development Center, O=Tencent Technology(Shenzhen) Company Limited, L=Shenzhen, ST=Guangdong, C=86`，SHA256 `0fe4ff85c215918396dadc7cd8ce6963339af33d37751a56e54c7206b63a3c7c`
- 资源比对基线：CN 8.0.79 / 3200 官方安装包 `weixin8079android3200_0x28004f30_arm64_1.apk`（SHA256 `f2a725bc04302ad218a563533ae79356e66b64aa711b275bc919a8d432f7e15d`）
- 上游检查：`SherlockChiang/WeChatMonet-CN` 最新提交为 `ee89e46`（Release `v26S4-CN14`，2026-11-03），仅覆盖到 Play 3182 与 CN 3200，尚未适配 CN 3220。
- 源 APK 摘要核对：`compat/3182.json` 与 `compat/3200.json` 中的 `sourceSha256` 为上游 `ee89e46` 重打包前的旧摘要；经逐项比对，当前 `files/*.apk` 除 `META-INF/` 与压缩/对齐封装外与 `2e47da4` 字节完全一致，已同步刷新三份映射中的 `sourceSha256`。

## 语义映射结果

通过全配置值、解析后 XML 树结构（展开内部资源引用编号）、XML/Style 槽位投票、连续 RID 块对齐与 DEX 字节码调用点定位，完成 CN 3200 → CN 3220 映射（证据详见 `compat/3220-audit.json`）：

| RRO | 目标条目 | 私有条目 | 说明 |
|---|---:|---:|---|
| MonetWeChat | 227 | 51 | 较 3200（228）减少 1 项已移除资源 `drawable/cbr` |
| MonetWeChatBadge | 2 | 0 | `color/Red_100`、`color/ac` |
| MonetWeChatChatBubble | 10 | 0 | `Link_80*`、`hu`、`hx`、`i_` 及 4 个 9-patch 气泡 |
| MonetWeChatMultiSceneCorners | 2 | 2 | `drawable/aj9`、`drawable/bw7`（及 2 个内部引用颜色） |
| MonetWeChatSolidTab | 1 | 0 | `color/bb` |
| MonetWeChatBlurTab | 2 | 0 | `color/bb`、`color/df` |

- 相比 3200 发生混淆改名的 7 项资源全部由结构与引用证据确认：
  - `color/ak8 → color/ak9`（唯一值 + XML 槽位 + 90 连续块）
  - `color/an4 → color/an5`（唯一值 + XML 槽位 + 138 连续块）
  - `color/an6 → color/an7`（唯一值 + 138 连续块 + DEX 引用）
  - `color/ans → color/ant`（唯一值 + XML 槽位 + 53 连续块）
  - `color/ao5 → color/ao7`（XML 布局 `layout/bl3` / `layout/eog` + 180 连续块）
  - `color/apf → color/aph`（17 候选，由 `Lwz4/k;->onBindViewHolder` DEX 调用点 + 75 连续块确认）
  - `drawable/dct → drawable/dd9`（2 候选，由 3 处 DEX 调用点 + 162 连续块确认）
- **消失资源说明（`drawable/cbr`）**：在 CN 3200 中为 `r/aj/cbr.webp`（300×580），仅被音乐 MV 编辑布局 `layout/c4w`、`layout/c54`（含 `MvTracksEditView`）的根 `RelativeLayout` 背景引用，无 ARSC 或 DEX 直接引用。CN 3220 已移除 `MvTracksEditView`、`layout/c4w`、`layout/c54`、`drawable/as0`–`as5` 与 `drawable/cbr`（`plugin/mv/` DEX 引用由 895 降至 69）。`MonetWeChat.apk` 内部无其他资源引用 `drawable/cbr`，故移入 `privateResources`（私有隔离），不影响 8.0.80 现有功能。

## 构建、对齐与签名验证（已完成）

- 六个 `files/*-3220.apk` 均已通过：
  - `resources.arsc` 未压缩（`ZIP_STORED`）且数据偏移按 4 字节对齐；
  - Android SDK `zipalign -c -p 4` 验证通过；
  - `apksigner verify` v3 签名验证通过；
  - 按类型重命名校验：全部资源 ID、配置值、内部引用与非 `resources.arsc` 文件字节与源包 100% 一致；全部目标资源存在于 CN 3220；全部私有条目重命名为 `compat_private_*` 且不与 CN 3220 冲突。
- Shell 语法检查（`sh -n`）、版本选择与防回退回归测试（`tests/test_version_selection.sh`）、二进制资源补丁单元测试（`tests/test_wx_patch.py`，3 项）及模块 ZIP CRC 校验全部通过。

## 签名变化与安装注意事项

- 原仓库/上游覆盖包私钥不可获得（`files/*.apk` 原为 `CN=Android Debug` 签名，SHA256 `595e889f...`）。本次生成的六个 `*-3220.apk` 使用独立本地开发密钥签名（`CN=WeChatMonet-CN Dev, O=WeChatMonet-CN, C=CN`，SHA256 `c3d63724bd8d88e5318a60076a3a4cf1a6e63a3a3df0ae8da8bae42743bfc5fc`），未借用任何其他项目密钥，签名证书与原包不同。
- 若手机此前已安装过旧版模块且系统 `/data/system/packages.xml` 中已登记过旧签名的 `monet.*` 静态 RRO 包，刷入后如遇 PackageManager 因签名变更拒绝更新扫描，建议先停用/卸载旧模块后重启一次，再刷入本模块并重启。

## 未进行真机检查（待手机验收）

- **本次仅完成本地适配、构建、资源表校验、签名校验与模块 ZIP 打包；未连接手机刷入模块、未重启设备、未进行真机 idmap 与浅色/深色界面实拍验收。**
- 实际视觉效果（主文字对比度、链接可读性、普通文本会话气泡、纯色/模糊底栏、红点与多场景圆角在 CN 8.0.80 明暗模式下的表现）尚待真机刷入重启后确认。
