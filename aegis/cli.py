import click
import os
import pyfiglet
import questionary
import hashlib
import subprocess
import platform
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule

# 禁用 OpenCV 警告信息，保持界面纯净
os.environ["OPENCV_LOG_LEVEL"] = "OFF"

from aegis.handlers.ppt import PPTHandler
from aegis.handlers.image import ImageHandler
from aegis.handlers.pdf import PDFHandler
from aegis.core.signature import SignatureManager
from aegis.core.sniffer import sniff_file_type
from aegis.core.database import TrackingDB
from aegis.core.mailer import Mailer

console = Console()
sig_mgr = SignatureManager()
db = TrackingDB()

def open_file(path):
    """跨平台打开文件"""
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', path])
        else:
            subprocess.call(['xdg-open', path])
    except Exception as e:
        console.print(f"[dim gray](Note: Could not auto-open file: {e})[/dim gray]")

MESSAGES = {
    "zh": {
        "title": "Aegis",
        "menu_prompt": "主菜单",
        "menu_embed": "单个嵌入 (Embed)",
        "menu_extract": "提取分析 (Extract)",
        "menu_distribute": "批量分发 (Distribute)",
        "menu_trace": "泄露溯源 (Trace)",
        "menu_identity": "身份与配置 (Settings)",
        "menu_exit": "退出程序 (Exit)",
        "menu_back": "BACK (返回上一级)",
        "path_input": "输入文件路径 (输入 ':b' 以回退)",
        "path_output": "保存结果为 (直接回车使用默认值, 输入 ':b' 以回退)",
        "path_recipients": "收件人列表文件 (txt) (输入 ':b' 以回退)",
        "watermark_text": "水印文本内容 (输入 ':b' 以回退)",
        "key_prompt": "设置密钥 (直接回车使用默认值, 输入 ':b' 以回退)",
        "processing": "处理中",
        "scanning": "正在识别格式并执行分析",
        "success_embed": "[SUCCESS] 嵌入成功",
        "fail_embed": "[ERROR] 嵌入失败",
        "report_title": "分析报告",
        "col_item": "字段",
        "col_info": "内容",
        "target_file": "分析对象",
        "key_fingerprint": "安全指纹",
        "status": "提取状态",
        "evidence": "结果路径",
        "note_title": "核验提示",
        "note_body": "请查看自动打开的证据图片。若文字轮廓清晰，则版权校验通过。",
        "fail_extract": "[ERROR] 分析失败: 未发现有效水印信号",
        "error_file": "[ERROR] 路径错误",
        "ident_name": "请输入姓名或机构名称 (输入 ':b' 以回退)",
        "ident_email": "请输入联系邮箱 (输入 ':b' 以回退)",
        "ident_success": "[SUCCESS] 身份证书创建成功",
        "ident_exists": "[WARNING] 身份已存在。是否重新创建？(将覆盖旧证书)",
        "sign_ask": "是否同时附加数字签名？(增强防篡改能力)",
        "sig_status": "数字签名",
        "sig_signer": "签署人",
        "sig_verified": "[VALID] 已验证 (完整性通过)",
        "sig_none": "[NONE] 未发现数字签名",
        "sig_fail": "[INVALID] 签名失效 (文件可能已被篡改)",
        "sniff_report": "识别真实格式",
        "test_mail_ask": "是否发送测试邮件验证配置？",
        "test_mail_success": "[SUCCESS] 测试邮件已发送",
        "test_mail_fail": "[ERROR] 邮件发送失败，请检查配置或授权码",
        "trace_prompt": "请输入证据图中显示的追踪 ID (输入 ':b' 以回退)",
        "trace_success": "[SUCCESS] 溯源成功",
        "trace_fail": "[ERROR] 数据库中未找到该 ID 的分发记录"
    },
    "en": {
        "title": "Aegis",
        "menu_prompt": "Main Menu",
        "menu_embed": "Single Embed",
        "menu_extract": "Extract & Analyze",
        "menu_distribute": "Batch Distribute",
        "menu_trace": "Trace & Audit",
        "menu_identity": "Identity & Config",
        "menu_exit": "Exit",
        "menu_back": "BACK (Return to previous)",
        "path_input": "File Path (Type ':b' to go back)",
        "path_output": "Save As (Enter for default, Type ':b' to go back)",
        "path_recipients": "Recipients File (Type ':b' to go back)",
        "watermark_text": "Watermark Text (Type ':b' to go back)",
        "key_prompt": "Secret Key (Enter for default, Type ':b' to go back)",
        "processing": "Processing",
        "scanning": "Sniffing & Analyzing",
        "success_embed": "[SUCCESS] Embedding completed",
        "fail_embed": "[ERROR] Embedding failed",
        "report_title": "Report",
        "col_item": "Item",
        "col_info": "Detail",
        "target_file": "Target",
        "key_fingerprint": "Key Fingerprint",
        "status": "Status",
        "evidence": "Evidence",
        "note_title": "NOTICE",
        "note_body": "Review the auto-opened image. Verification passed if text is visible.",
        "fail_extract": "[ERROR] Failed: No watermark detected",
        "error_file": "[ERROR] Invalid path",
        "ident_name": "Enter name or organization (Type ':b' to go back)",
        "ident_email": "Enter contact email (Type ':b' to go back)",
        "ident_success": "[SUCCESS] Identity certificate created",
        "ident_exists": "[WARNING] Identity already exists. Overwrite?",
        "sign_ask": "Add digital signature? (Anti-tamper)",
        "sig_status": "Digital Signature",
        "sig_signer": "Signer",
        "sig_verified": "[VALID] Verified (Integrity Passed)",
        "sig_none": "[NONE] No signature found",
        "sig_fail": "[INVALID] Invalid (File might be tampered)",
        "sniff_report": "Detected Format",
        "test_mail_ask": "Send a test email to verify config?",
        "test_mail_success": "[SUCCESS] Test email sent",
        "test_mail_fail": "[ERROR] Failed to send email",
        "trace_prompt": "Enter the tracking ID (Type ':b' to go back)",
        "trace_success": "[SUCCESS] Trace success",
        "trace_fail": "[ERROR] No distribution record found for this ID"
    }
}

CURRENT_LANG = "zh"

def print_banner():
    """极致简约 Banner"""
    ascii_art = pyfiglet.figlet_format("Aegis", font="slant")
    console.print(Rule(style="blue"))
    console.print(Align.center(Text(ascii_art, style="bold cyan")))
    console.print(Rule(style="blue"))
    console.print()

def interactive_menu():
    """全功能交互式主菜单 - 状态机模式"""
    global CURRENT_LANG
    
    # 语言选择
    lang_choice = questionary.select(
        "Language / 语言",
        choices=["简体中文", "English"],
        qmark=">"
    ).ask()
    
    if lang_choice is None: return
    CURRENT_LANG = "zh" if lang_choice == "简体中文" else "en"
    msg = MESSAGES[CURRENT_LANG]
    
    print_banner()
    
    while True:
        action = questionary.select(
            msg["menu_prompt"],
            choices=[
                msg["menu_embed"],
                msg["menu_extract"],
                msg["menu_distribute"],
                msg["menu_trace"],
                msg["menu_identity"],
                msg["menu_exit"]
            ],
            qmark=">",
            style=questionary.Style([
                ('pointer', 'fg:cyan bold'),
                ('highlighted', 'fg:cyan bold'),
                ('selected', 'fg:green'),
            ])
        ).ask()

        if action is None or "Exit" in action or "退出" in action:
            break
        
        # 路由分发
        if msg["menu_embed"] in action:
            run_embed_wizard()
        elif msg["menu_extract"] in action:
            run_extract_wizard()
        elif msg["menu_distribute"] in action:
            run_distribute_wizard()
        elif msg["menu_trace"] in action:
            run_trace_wizard()
        elif msg["menu_identity"] in action:
            run_settings_wizard()

def get_input(prompt, default=None, path=False):
    """通用输入处理，支持 :b 回退"""
    if path:
        val = questionary.path(prompt, default="" if default is None else default, qmark=">").ask()
    else:
        val = questionary.text(prompt, default="" if default is None else default, qmark=">").ask()
    
    if val == ":b": return ":b"
    if val == "" and default is not None: return default
    return val

def run_embed_wizard():
    """嵌入向导：参数输入 -> 确认页 -> 执行"""
    msg = MESSAGES[CURRENT_LANG]
    
    # 1. 收集参数
    input_file = get_input(msg["path_input"], path=True)
    if input_file == ":b" or not input_file: return
    
    default_out = input_file + "_protected" + (".pdf" if input_file.lower().endswith('.pdf') else ".png")
    output_file = get_input(msg["path_output"], default=default_out)
    if output_file == ":b": return
    
    text = get_input(msg["watermark_text"])
    if text == ":b": return
    
    key = get_input(msg["key_prompt"], default="1")
    if key == ":b": return
    
    # 2. 身份选择
    ident_id = None
    should_sign = False
    if sig_mgr.has_identity():
        identities = sig_mgr.list_identities()
        if len(identities) > 1:
            # 多身份选择
            choices = identities + ["None (No Signature)"]
            choice = questionary.select("Select Identity:", choices=choices, qmark=">").ask()
            if choice != "None (No Signature)":
                ident_id = choice
                should_sign = True
        else:
            # 单身份确认
            if questionary.confirm(msg["sign_ask"], default=True, qmark=">").ask():
                should_sign = True
                ident_id = identities[0]

    # 3. 确认页 (Confirmation Page)
    console.print()
    table = Table(title="Task Confirmation", show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("Input", input_file)
    table.add_row("Output", output_file)
    table.add_row("Watermark", text)
    table.add_row("Identity", ident_id if should_sign else "None")
    console.print(table)
    console.print()
    
    if not questionary.confirm("Start processing?", default=True, qmark=">").ask():
        return # 用户取消

    run_embed(input_file, output_file, text, key, should_sign=should_sign, ident_id=ident_id)

def run_extract_wizard():
    msg = MESSAGES[CURRENT_LANG]
    input_file = get_input(msg["path_input"], path=True)
    if input_file == ":b" or not input_file: return
    
    key = get_input(msg["key_prompt"], default="1")
    if key == ":b": return
    
    output = input_file + "_evidence.png"
    run_extract(input_file, output, key)

def run_distribute_wizard():
    msg = MESSAGES[CURRENT_LANG]
    input_file = get_input(msg["path_input"], path=True)
    if input_file == ":b" or not input_file: return
    
    recipients = get_input(msg["path_recipients"], path=True)
    if recipients == ":b" or not recipients: return
    
    text_tpl = get_input(msg["watermark_text"] + " (ID: {})", default="ID: {}")
    if text_tpl == ":b": return
    
    key = get_input(msg["key_prompt"], default="1")
    if key == ":b": return
    
    subject = get_input("Subject / 邮件主题", default="Protected File Delivery")
    if subject == ":b": return
    
    ctx = click.get_current_context()
    ctx.invoke(distribute, input=input_file, recipients=recipients, template=text_tpl, key=key, subject=subject)

def run_trace_wizard():
    msg = MESSAGES[CURRENT_LANG]
    input_file = get_input(msg["path_input"], path=True)
    if input_file == ":b" or not input_file: return
    
    key = get_input(msg["key_prompt"], default="1")
    if key == ":b": return
    
    ctx = click.get_current_context()
    ctx.invoke(trace, input=input_file, key=key)

def run_settings_wizard():
    """设置菜单：身份管理与配置"""
    msg = MESSAGES[CURRENT_LANG]
    
    while True:
        choices = []
        if CURRENT_LANG == "zh": 
            choices = ["新建身份证书 (RSA)", "配置分发邮箱 (SMTP)", msg["menu_back"]]
        else: 
            choices = ["Create New Identity (RSA)", "Configure Mailer (SMTP)", msg["menu_back"]]
        
        sub_action = questionary.select("Settings:", choices=choices, qmark=">").ask()
        
        if sub_action is None or msg["menu_back"] in sub_action:
            break
            
        if "RSA" in sub_action:
            # 检查已有身份
            identities = sig_mgr.list_identities()
            new_id = None
            if identities:
                console.print(f"[yellow]Existing identities: {', '.join(identities)}[/yellow]")
                if questionary.confirm("Create an additional identity?", default=False).ask():
                    new_id = questionary.text("Enter ID for new identity (e.g., 'work'):").ask()
                    if not new_id: continue
                else:
                    continue # 不覆盖，直接返回

            name = get_input(msg["ident_name"])
            if name == ":b": continue
            email = get_input(msg["ident_email"])
            if email == ":b": continue
            
            with console.status("[bold green]Generating RSA-4096 cryptographic identity...[/bold green]"):
                sig_mgr.create_identity(name, email, ident_id=new_id)
            console.print(f"[bold green]{msg['ident_success']}[/bold green]")
            
        else:
            ctx = click.get_current_context()
            ctx.invoke(config)

def run_embed(input, output, text, key, should_sign=False, ident_id=None):
    """执行嵌入核心逻辑"""
    msg = MESSAGES[CURRENT_LANG]
    # 使用嗅探器识别格式
    f_type = sniff_file_type(input)
    
    with console.status(f"[bold green]{msg['processing']}[/bold green]...", spinner="dots"):
        try:
            if f_type == 'ppt':
                handler = PPTHandler()
                success = handler.process(input, output, text, key=key)
            elif f_type == 'pdf':
                handler = PDFHandler()
                success = handler.process(input, output, text, key=key)
            elif f_type == 'image':
                handler = ImageHandler()
                success = handler.process(input, output, text, key=key)
            else:
                # Fallback 到后缀判断
                ext = input.lower().split('.')[-1]
                if ext == 'pptx':
                    handler = PPTHandler()
                    success = handler.process(input, output, text, key=key)
                elif ext in ['png', 'jpg', 'jpeg', 'bmp']:
                    handler = ImageHandler()
                    success = handler.process(input, output, text, key=key)
                else:
                    success = False
            
            if success and should_sign:
                handler.attach_signature(output, sig_mgr, ident_id=ident_id)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            success = False

    if success:
        res_text = Text(f"{msg['success_embed']} ", style="bold green")
        res_text.append(output, style="underline cyan")
        console.print(res_text)
    else:
        console.print(f"[bold red]{msg['fail_embed']}[/bold red]")

def run_extract(input, output, key):
    """执行提取核心逻辑"""
    msg = MESSAGES[CURRENT_LANG]
    # 使用嗅探器识别格式
    f_type = sniff_file_type(input)
    result = None
    sig_status = "none"
    sig_info = None

    with console.status(f"[bold blue]{msg['scanning']}[/bold blue]...", spinner="earth"):
        try:
            temp_handler = ImageHandler() 
            sig_status, sig_info = temp_handler.get_signature(input, sig_mgr)

            if f_type == 'ppt':
                handler = PPTHandler()
                result = handler.extract(input, key=key)
            elif f_type == 'pdf':
                handler = PDFHandler()
                result = handler.extract(input, output_wm_path=output, key=key)
            elif f_type == 'image' or sig_status != "none":
                handler = ImageHandler()
                result = handler.extract(input, output_wm_path=output, key=key)
            else:
                ext = input.lower().split('.')[-1]
                if ext == 'pptx':
                    handler = PPTHandler()
                    result = handler.extract(input, key=key)
                elif ext in ['png', 'jpg', 'jpeg', 'bmp']:
                    handler = ImageHandler()
                    result = handler.extract(input, output_wm_path=output, key=key)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sig_status = "error"

    console.print()
    
    if result and os.path.exists(result):
        table = Table(title=msg["report_title"], show_header=True, header_style="bold magenta")
        table.add_column(msg["col_item"], style="cyan")
        table.add_column(msg["col_info"], style="green")

        table.add_row(msg["target_file"], os.path.basename(input))
        table.add_row(msg["sniff_report"], f_type.upper() if f_type != 'unknown' else "AUTO")
        table.add_row(msg["key_fingerprint"], f"SHA256(***{key[-3:] if len(key) >= 3 else key})")
        
        if sig_status == "valid" and sig_info:
            table.add_row(msg["sig_status"], msg["sig_verified"])
            table.add_row(msg["sig_signer"], f"{sig_info['name']} <{sig_info['email']}>")
        elif sig_status == "invalid":
            table.add_row(msg["sig_status"], f"[bold red]{msg['sig_fail']}[/bold red]")
        else:
            table.add_row(msg["sig_status"], f"[gray]{msg['sig_none']}[/gray]")

        table.add_row(msg["status"], "SUCCESS")
        table.add_row(msg["evidence"], result)

        console.print(table)
        console.print(Panel(f"[bold yellow]{msg['note_title']}:[/bold yellow] {msg['note_body']}", border_style="yellow"))
        
        # 体验增强：自动打开证据图
        open_file(result)
    else:
        console.print(Panel(msg["fail_extract"], border_style="red"))

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Aegis: Blind Watermarking & Digital Signature Tool."""
    if ctx.invoked_subcommand is None:
        interactive_menu()

@main.command()
@click.option('--input', '-i', required=True, help="Path to the source file (Image/PDF/PPTX).")
@click.option('--output', '-o', help="Path to save the protected file. (Defaults to [in]_protected.png/pdf)")
@click.option('--text', '-t', required=True, help="Watermark text to embed.")
@click.option('--key', '-k', default="1", help="Security key for blind watermarking. (Default: 1)")
def embed(input, output, text, key):
    """Embed invisible watermark and optional digital signature."""
    if not output:
        output = input + "_protected" + (".pdf" if input.lower().endswith('.pdf') else ".png")
    print_banner()
    run_embed(input, output, text, key)

@main.command()
@click.option('--input', '-i', required=True, help="Path to the protected file.")
@click.option('--output', '-o', help="Path to save the evidence image. (Defaults to [in]_evidence.png)")
@click.option('--key', '-k', default="1", help="Security key used during embedding.")
def extract(input, output, key):
    """Extract and analyze watermark/signature from a file."""
    if not output:
        output = input + "_evidence.png"
    print_banner()
    run_extract(input, output, key)

@main.command()
@click.option('--input', '-i', required=True, help="Original file to distribute (Image/PDF/PPTX).")
@click.option('--recipients', '-r', required=True, help="A text file containing one email address per line.")
@click.option('--template', '-t', default="ID: {}", help="Template for watermark. '{}' will be replaced by unique ID.")
@click.option('--key', '-k', default="1", help="Security key for watermarking.")
@click.option('--subject', '-s', default="Protected File Delivery", help="Email subject.")
def distribute(input, recipients, template, key, subject):
    """Batch distribute personalized files with unique tracking IDs."""
    import uuid
    
    cfg_path = os.path.join(os.path.expanduser("~"), ".aegis_identity", "config.json")
    if not os.path.exists(cfg_path):
        console.print("[red]SMTP not configured. Run 'aegis config' first.[/red]")
        return
    
    with open(cfg_path, 'r') as f:
        cfg = json.load(f)
    
    mailer = Mailer(cfg['smtp_server'], cfg['smtp_port'], cfg['sender_email'], cfg['password'])
    
    if not os.path.exists(recipients):
        console.print(f"[red]Recipients file not found: {recipients}[/red]")
        return

    try:
        with open(recipients, 'r', encoding='utf-8') as f:
            email_list = [line.strip() for line in f if "@" in line]
    except UnicodeDecodeError:
        with open(recipients, 'r') as f:
            email_list = [line.strip() for line in f if "@" in line]

    print_banner()
    console.print(f"[*] Starting Batch Distribution for {len(email_list)} recipients...")

    for email in email_list:
        dist_id = uuid.uuid4().hex[:8].upper()
        wm_text = template.replace("{}", dist_id)
        # 更加规范的临时文件名
        base, ext = os.path.splitext(os.path.basename(input))
        temp_output = f"dist_{dist_id}_{base}{ext}"
        
        console.print(f"[*] Processing for [cyan]{email}[/cyan] (ID: {dist_id})...")
        log_id = db.log_distribution(os.path.basename(input), email, dist_id, key)
        
        f_type = sniff_file_type(input)
        if f_type == 'ppt': handler = PPTHandler()
        elif f_type == 'pdf': handler = PDFHandler()
        else: handler = ImageHandler()
        
        if handler.process(input, temp_output, wm_text, key=key):
            body = f"Hello,\n\nPlease find the protected document attached.\n\nVerify ID: {dist_id}\n\nRegards,\nAegis System"
            success = mailer.send_protected_file(email, temp_output, subject, body)
            if success:
                db.update_status(log_id, "SUCCESS")
                console.print(f"  [green]Email sent successfully.[/green]")
            else:
                db.update_status(log_id, "MAIL_FAILED")
        else:
            db.update_status(log_id, "EMBED_FAILED")
        
        if os.path.exists(temp_output): os.remove(temp_output)

@main.command()
@click.option('--input', '-i', required=True, help="Path to the leaked file.")
@click.option('--key', '-k', default="1", help="Security key used during distribution.")
def trace(input, key):
    """Trace a leaked file back to its recipient using the tracking database."""
    print_banner()
    base, _ = os.path.splitext(os.path.basename(input))
    temp_wm = f"trace_{base}_evidence.png"
    
    f_type = sniff_file_type(input)
    if f_type == 'ppt': handler = PPTHandler()
    elif f_type == 'pdf': handler = PDFHandler()
    else: handler = ImageHandler()
    
    result_path = handler.extract(input, output_wm_path=temp_wm, key=key)
    
    if result_path and os.path.exists(result_path):
        open_file(result_path)
        console.print(f"[yellow]Watermark extracted to {result_path} (Auto-opened).[/yellow]")
        dist_id = questionary.text("Enter the tracking ID identified in the image:").ask()
        
        if dist_id:
            record = db.find_by_watermark(dist_id)
            if record:
                table = Table(title="Trace Results", header_style="bold magenta")
                table.add_column("Field")
                table.add_column("Value")
                table.add_row("Recipient", f"[bold green]{record[2]}[/bold green]")
                table.add_row("Original File", record[1])
                table.add_row("Timestamp", str(record[5]))
                table.add_row("Status", record[6])
                console.print(table)
            else:
                console.print("[red]No matching distribution record found in database.[/red]")
    else:
        console.print("[red]Failed to extract watermark signal.[/red]")

@main.command()
def config():
    """Setup SMTP credentials and test the connection."""
    msg = MESSAGES[CURRENT_LANG]
    data = {}
    data['smtp_server'] = questionary.text("SMTP Server (e.g., smtp.qq.com):", default="smtp.qq.com").ask()
    data['smtp_port'] = int(questionary.text("SMTP Port (e.g., 465):", default="465").ask())
    data['sender_email'] = questionary.text("Sender Email:").ask()
    data['password'] = questionary.password("SMTP Password/Auth Code:").ask()
    
    cfg_path = os.path.join(os.path.expanduser("~"), ".aegis_identity", "config.json")
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    with open(cfg_path, 'w') as f:
        json.dump(data, f)
    console.print("[green][SUCCESS] Configuration saved[/green]")
    
    if questionary.confirm(msg["test_mail_ask"], default=True).ask():
        mailer = Mailer(data['smtp_server'], data['smtp_port'], data['sender_email'], data['password'])
        with console.status("[bold blue]Sending test email...[/bold blue]"):
            success = mailer.send_protected_file(data['sender_email'], cfg_path, "Aegis Config Test", "If you receive this, your SMTP config is correct.")
        
        if success: console.print(f"[bold green]{msg['test_mail_success']}[/bold green]")
        else: console.print(f"[bold red]{msg['test_mail_fail']}[/bold red]")

if __name__ == '__main__':
    main()