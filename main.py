import os
import fitz
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        return

    if not update.message.document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Mandami un PDF.")
        return

    file = await context.bot.get_file(update.message.document.file_id)
    input_path = "input.pdf"
    output_path = "cleaned.pdf"

    await file.download_to_drive(input_path)

    doc = fitz.open(input_path)
    new_doc = fitz.open()

    for page in doc:
        text_top = page.get_text(
            "text",
            clip=fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.2)
        ).lower()

        if "credit switch" in text_top or "report medium" in text_top:
            top_crop = 0.12
        elif "report b2b" in text_top:
            top_crop = 0.07
        else:
            top_crop = 0.10

        bottom_crop = 0.10
        left_crop = 0.06

        rect = fitz.Rect(
            page.rect.width * left_crop,
            page.rect.height * top_crop,
            page.rect.width,
            page.rect.height * (1 - bottom_crop)
        )

        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        new_page.show_pdf_page(new_page.rect, doc, page.number, clip=rect)

    new_doc.save(output_path)

    await update.message.reply_document(InputFile(output_path), filename="pulito.pdf")

    doc.close()
    new_doc.close()
    os.remove(input_path)
    os.remove(output_path)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_pdf))

app.run_polling()
