import click
import os
import pyfiglet
import questionary
import hashlib
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

# --- 多语言配置 ---
MESSAGES = {
    "zh": {
        "title": "Aegis",
        "menu_prompt": "主菜单",
        "menu_embed": "嵌入水印 (Embed)",
        "menu_extract": "提取分析 (Extract)",
        "menu_identity": "身份管理 (Identity)",
        "menu_exit": "退出程序 (Exit)",
        "path_input": "输入文件路径",
        "path_output": "保存结果为",
        "watermark_text": "水印文本内容",
        "key_prompt": "设置密钥 (不填则默认为 1)",
        "processing": "处理中",
        "scanning": "识别格式并分析中",
        "success_embed": "嵌入成功!",
        "fail_embed": "嵌入失败。",
        "report_title": "分析报告",
        "col_item": "字段",
        "col_info": "内容",
        "target_file": "分析对象",
        "key_fingerprint": "安全指纹",
        "status": "提取状态",
        "evidence": "结果路径",
        "note_title": "核验提示",
        "note_body": "请查看结果图片。若文字轮廓清晰，则版权校验通过。",
        "fail_extract": "分析失败: 未发现有效水印信号。",
        "error_file": "路径错误，请重新输入。",
        "ident_name": "请输入您的真实姓名/机构名",
        "ident_email": "请输入您的联系邮箱",
        "ident_success": "✅ 身份证书创建成功!",
        "ident_exists": "⚠️ 身份已存在。是否重新创建？(将覆盖旧证书)",
        "sign_ask": "是否同时附加数字签名？(增强防篡改能力)",
        "sig_status": "数字签名",
        "sig_signer": "签署人",
        "sig_verified": "✅ 已验证 (完整性通过)",
        "sig_none": "未发现数字签名",
        "sig_fail": "❌ 签名失效 (文件可能已被篡改)",
        "sniff_report": "识别真实格式"
    },
    "en": {
        "title": "Aegis",
        "menu_prompt": "Main Menu",
        "menu_embed": "Embed Watermark",
        "menu_extract": "Extract & Analyze",
        "menu_identity": "Manage Identity",
        "menu_exit": "Exit",
        "path_input": "File Path",
        "path_output": "Save As",
        "watermark_text": "Watermark Text",
        "key_prompt": "Secret Key (Default: 1)",
        "processing": "Processing",
        "scanning": "Sniffing Format & Analyzing",
        "success_embed": "Success!",
        "fail_embed": "Failed.",
        "report_title": "Report",
        "col_item": "Item",
        "col_info": "Detail",
        "target_file": "Target",
        "key_fingerprint": "Key Fingerprint",
        "status": "Status",
        "evidence": "Evidence",
        "note_title": "NOTICE",
        "note_body": "Verification passed if text outlines are visible.",
        "fail_extract": "Failed: No watermark detected.",
        "error_file": "Invalid path.",
        "ident_name": "Enter your name or organization",
        "ident_email": "Enter your email",
        "ident_success": "✅ Identity certificate created!",
        "ident_exists": "⚠️ Identity already exists. Overwrite?",
        "sign_ask": "Add digital signature as well? (Anti-tamper)",
        "sig_status": "Digital Signature",
        "sig_signer": "Signer",
        "sig_verified": "✅ Verified (Integrity Passed)",
        "sig_none": "No signature found",
        "sig_fail": "❌ Invalid (File might be tampered)",
        "sniff_report": "Detected Format"
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
    """交互式主菜单"""
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
        
        if "Embed" in action or "嵌入" in action:
            input_file = questionary.path(msg["path_input"] + ":", qmark=">").ask()
            if not input_file or not os.path.exists(input_file):
                console.print(f"[red]{msg['error_file']}[/red]")
                continue
            
            output_file = questionary.text(msg["path_output"] + ":", default=input_file + "_protected.png", qmark=">").ask()
            text = questionary.text(msg["watermark_text"] + ":", qmark=">").ask()
            key = questionary.text(msg["key_prompt"] + ":", qmark=">").ask()
            if not key: key = "1"
            
            should_sign = False
            if sig_mgr.has_identity():
                should_sign = questionary.confirm(msg["sign_ask"], default=True, qmark=">").ask()
            
            run_embed(input_file, output_file, text, key, should_sign=should_sign)
            
        elif "Extract" in action or "提取" in action:
            input_file = questionary.path(msg["path_input"] + ":", qmark=">").ask()
            if not input_file or not os.path.exists(input_file):
                console.print(f"[red]{msg['error_file']}[/red]")
                continue
                
            key = questionary.text(msg["key_prompt"] + ":", qmark=">").ask()
            if not key: key = "1"
            output = input_file + "_wm.png"
            
            run_extract(input_file, output, key)

        elif "Identity" in action or "身份" in action:
            run_identity_setup()

def run_identity_setup():
    """设置或更新身份信息"""
    msg = MESSAGES[CURRENT_LANG]
    if sig_mgr.has_identity():
        if not questionary.confirm(msg["ident_exists"], default=False, qmark=">").ask():
            return

    name = questionary.text(msg["ident_name"] + ":", qmark=">").ask()
    email = questionary.text(msg["ident_email"] + ":", qmark=">").ask()
    
    if name and email:
        with console.status("[bold green]Generating RSA-4096 Keys...[/bold green]"):
            sig_mgr.create_identity(name, email)
        console.print(f"[bold green]{msg['ident_success']}[/bold green]")

def run_embed(input, output, text, key, should_sign=False):
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
                # Fallback 到后缀判断（针对未识别但可能合法的格式）
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
                handler.attach_signature(output, sig_mgr)

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
            # 无论嗅探结果如何，先尝试读取签名（这是反伪装的第一步）
            # 这里的 handler 只是为了调用 get_signature，逻辑是通用的
            temp_handler = ImageHandler() 
            sig_status, sig_info = temp_handler.get_signature(input, sig_mgr)

            if f_type == 'ppt':
                handler = PPTHandler()
                result = handler.extract(input, key=key)
            elif f_type == 'pdf':
                handler = PDFHandler()
                result = handler.extract(input, output_wm_path=output, key=key)
            elif f_type == 'image' or sig_status != "none":
                # 如果是图片，或者包含我们的签名，强制尝试图片模式
                handler = ImageHandler()
                result = handler.extract(input, output_wm_path=output, key=key)
            else:
                # 最后的保底：看后缀
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
    else:
        console.print(Panel(msg["fail_extract"], border_style="red"))

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Aegis: 隐形水印保护工具"""
    if ctx.invoked_subcommand is None:
        interactive_menu()
    else:
        pass

@main.command()
@click.option('--input', '-i', required=True)
@click.option('--output', '-o', required=True)
@click.option('--text', '-t', required=True)
@click.option('--key', '-k', default="1", type=str)
def embed(input, output, text, key):
    """Embed mode"""
    print_banner()
    run_embed(input, output, text, key)

@main.command()
@click.option('--input', '-i', required=True)
@click.option('--output', '-o')
@click.option('--key', '-k', default="1", type=str)
def extract(input, output, key):
    """Extract mode"""
    print_banner()
    run_extract(input, output, key)

@main.command()
@click.option('--input', '-i', required=True, help="Original file to distribute")
@click.option('--recipients', '-r', required=True, help="Recipients file (one email per line)")
@click.option('--template', '-t', default="ID: {}", help="Watermark text template ({} will be replaced by ID)")
@click.option('--key', '-k', default="1")
@click.option('--subject', '-s', default="File Share")
def distribute(input, recipients, template, key, subject):
    """Batch distribute personalized protected files via Email."""
    import uuid
    import json
    
    # 尝试加载配置 (简单存储在 .aegis_identity/config.json)
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

    with open(recipients, 'r') as f:
        email_list = [line.strip() for line in f if "@" in line]

    print_banner()
    console.print(f"[*] Starting Batch Distribution for {len(email_list)} recipients...")

    for email in email_list:
        dist_id = uuid.uuid4().hex[:8].upper()
        wm_text = template.replace("{}", dist_id)
        temp_output = f"dist_{dist_id}_{os.path.basename(input)}"
        
        console.print(f"[*] Processing for [cyan]{email}[/cyan] (ID: {dist_id})...")
        
        # 记录到数据库
        log_id = db.log_distribution(os.path.basename(input), email, dist_id, key)
        
        # 嵌入水印
        f_type = sniff_file_type(input)
        if f_type == 'ppt': handler = PPTHandler()
        elif f_type == 'pdf': handler = PDFHandler()
        else: handler = ImageHandler()
        
        if handler.process(input, temp_output, wm_text, key=key):
            success = mailer.send_protected_file(email, temp_output, subject, f"Please find the protected file attached. Your unique ID is {dist_id}")
            if success:
                db.update_status(log_id, "SUCCESS")
                console.print(f"  [green]✓ Email sent successfully.[/green]")
            else:
                db.update_status(log_id, "MAIL_FAILED")
        else:
            db.update_status(log_id, "EMBED_FAILED")
        
        if os.path.exists(temp_output): os.remove(temp_output)

@main.command()
@click.option('--input', '-i', required=True, help="Leaked file to trace")
@click.option('--key', '-k', default="1")
def trace(input, key):
    """Trace the distribution history of a leaked file."""
    print_banner()
    temp_wm = "trace_extract.png"
    
    f_type = sniff_file_type(input)
    if f_type == 'ppt': handler = PPTHandler()
    elif f_type == 'pdf': handler = PDFHandler()
    else: handler = ImageHandler()
    
    result_path = handler.extract(input, output_wm_path=temp_wm, key=key)
    
    if result_path and os.path.exists(result_path):
        # 这里需要用户查看提取出的文字，或者我们尝试 OCR（由于盲水印目前主要是视觉确认，我们提示用户输入 ID）
        console.print("[yellow]Watermark extracted to trace_extract.png. Please identify the ID in the image.[/yellow]")
        dist_id = questionary.text("Enter the ID identified in the evidence image:").ask()
        
        if dist_id:
            record = db.find_by_watermark(dist_id)
            if record:
                table = Table(title="Trace Results", header_style="bold magenta")
                table.add_column("Field")
                table.add_column("Value")
                table.add_row("Recipient", f"[bold green]{record[2]}[/bold green]")
                table.add_row("Original File", record[1])
                table.add_row("Timestamp", record[5])
                table.add_row("Status", record[6])
                console.print(table)
            else:
                console.print("[red]No matching distribution record found in database.[/red]")
    else:
        console.print("[red]Failed to extract watermark signal.[/red]")

@main.command()
def config():
    """Configure SMTP settings for distribution."""
    import json
    data = {}
    data['smtp_server'] = questionary.text("SMTP Server (e.g., smtp.qq.com):").ask()
    data['smtp_port'] = int(questionary.text("SMTP Port (e.g., 465):").ask())
    data['sender_email'] = questionary.text("Sender Email:").ask()
    data['password'] = questionary.password("SMTP Password/Auth Code:").ask()
    
    cfg_path = os.path.join(os.path.expanduser("~"), ".aegis_identity", "config.json")
    with open(cfg_path, 'w') as f:
        json.dump(data, f)
    console.print("[green]Configuration saved![/green]")

if __name__ == '__main__':
    main()
