import discord
import random
import string
import requests
import time
from discord.ext import commands
from discord import app_commands, ui
import os
from dotenv import load_dotenv
load_dotenv()
from server import server_on

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== Function สำหรับสร้างชื่อ
def generate_username(case):
    letters_set = string.ascii_lowercase if case == "lower" else string.ascii_uppercase
    first_letter = random.choice(letters_set)
    number = str(random.randint(0, 9))
    letters = ''.join(random.choices(letters_set, k=2))
    return f"{first_letter}_{number}{letters}"

# ===== Modal สำหรับรับข้อมูลจากผู้ใช้
class UsernameCheckModal(ui.Modal, title="🔍 Roblox Username Checker"):
    amount = ui.TextInput(label="จำนวนชื่อที่ต้องการเช็ค", placeholder="เช่น 10", required=True)
    delay = ui.TextInput(label="ดีเลย์ (ms) ระหว่างแต่ละรอบ", placeholder="เช่น 300", required=True)
    case = ui.TextInput(label="พิมพ์เล็กหรือใหญ่ (พิม 'lower' หรือ 'upper')", placeholder="lower หรือ upper", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            amount = int(self.amount.value)
            delay = int(self.delay.value) / 1000
            case_type = self.case.value.lower()

            if case_type not in ['lower', 'upper']:
                await interaction.followup.send("❌ ต้องกรอก 'lower' หรือ 'upper' เท่านั้น", ephemeral=True)
                return

            valid_usernames = []
            for _ in range(amount):
                username = generate_username(case_type)
                url = f"https://auth.roblox.com/v2/usernames/validate?request.username={username}&request.birthday=2000-01-01&request.context=Signup"
                try:
                    res = requests.get(url)
                    data = res.json()
                    if data.get("message") == "Username is valid":
                        valid_usernames.append(username)
                except:
                    pass
                time.sleep(delay)

            if valid_usernames:
                embed = discord.Embed(
                    title="✅ Valid Roblox Usernames",
                    description="\n".join([f"`{u}`" for u in valid_usernames]),
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
                # embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/889976848581287946/1193140899987865600/Herrscher.of.the.Void.full.2866346.gif?ex=65aba20e&is=65992d0e&hm=9afd68f45f0972ffadbaf18375adb52cf6e80cf59d83bbf6c0ecf1ca6e51a1e9&')
                ima = "https://i.gifer.com/7efs.gif"
                embed.set_image(url=ima)

                try:
                    await interaction.user.send(embed=embed)
                    await interaction.followup.send("✅ ส่งชื่อที่ใช้ได้ให้ทาง DM แล้ว!", ephemeral=True)
                except discord.Forbidden:
                    await interaction.followup.send("❌ ไม่สามารถส่ง DM ได้ กรุณาเปิด DM ก่อน", ephemeral=True)
            else:
                await interaction.followup.send("❌ ไม่พบชื่อที่ใช้ได้เลย", ephemeral=True)

        except ValueError:
            await interaction.followup.send("❌ โปรดกรอกตัวเลขให้ถูกต้อง", ephemeral=True)

# ===== ปุ่ม Start ที่เปิด Modal
class StartButton(ui.View):
    @ui.button(label="🚀 Start", style=discord.ButtonStyle.primary)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(UsernameCheckModal())

# ===== คำสั่ง /setup
@bot.tree.command(name="setup", description="แสดงหน้าเริ่มต้นของบอท")
async def setup(interaction: discord.Interaction):

    username = interaction.user.display_name  # ใช้ interaction แทน ctx      

    embed = discord.Embed(title="\nRoblox Check User", description=f"**บริการสุ่มชื่อ Roblox + ชื่อที่สามารถใช้งานได้ !**", color=0x000000)
    embed.set_author(name=username)
    embed.add_field(name="- 📄Roblox Username Checker", value="ตรวจสอบชื่อ Roblox ที่ยังว่างอยู่ได้อย่างง่ายดาย! \n คลิกปุ่ม Start ด้านล่างเพื่อเริ่มกรอกข้อมูลแล้วให้บอทสุ่มชื่อให้คุณได้เลย 🎲",inline=False)
    embed.set_image(url="https://www.icegif.com/wp-content/uploads/2023/04/icegif-627.gif")
    embed.set_footer(text="Powered by Balthazar")
    await interaction.response.send_message(embed=embed, view=StartButton())

# ===== บอทพร้อมใช้งาน
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot is online as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(name='ระบบเช็กชื่อ Roblox', url='https://www.twitch.tv/kerlf'))
        try:
        with open('image.gif', 'rb') as avatar:
            await client.user.edit(avatar=avatar.read())
        print('Animated avatar uploaded successfully!')
    except Exception as e:
        print("Failed to upload animated avatar:", e)

server_on()  # เรียกใช้ฟังก์ชัน server_on เพื่อเริ่มเซิร์ฟเวอร์ Flask

bot.run(os.getenv("TOKEN"))  # ใช้ TOKEN จาก environment variable
