from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
import time
import json

app = Flask(__name__)
app.secret_key = "blockchain-demo"

class Block:
    def __init__(self, index, previous_hash, transactions, timestamp=None, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.index}{self.previous_hash}{json.dumps(self.transactions, sort_keys=True)}{self.timestamp}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.chain = [Block(0, "0", [{"from": "Genesis", "to": "Genesis", "amount": 0}])]
        self.pending_transactions = []

    def add_transaction(self, sender, receiver, amount):
        self.pending_transactions.append({
            "from": sender,
            "to": receiver,
            "amount": amount
        })

    def mine(self):
        if not self.pending_transactions:
            return False
        block = Block(
            len(self.chain),
            self.chain[-1].hash,
            self.pending_transactions.copy()
        )
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = []
        return True

    def is_valid(self):
        for i, block in enumerate(self.chain):
            if block.hash != block.calculate_hash():
                return False
            if i > 0:
                if block.previous_hash != self.chain[i - 1].hash:
                    return False
                if not block.hash.startswith("0" * self.difficulty):
                    return False
        return True


blockchain = Blockchain()

@app.route("/")
def home():
    latest_block = blockchain.chain[-1]
    return render_template(
        "index.html",
        latest=latest_block,
        blocks=blockchain.chain,
        pending=blockchain.pending_transactions,
        valid=blockchain.is_valid()
    )

@app.route("/submit", methods=["POST"])
def submit():
    sender = request.form.get("nama1", "").strip()
    receiver = request.form.get("nama2", "").strip()
    amount = request.form.get("uang", "").strip()

    if not sender or not receiver or sender == receiver:
        flash("Pilih Nama 1 dan Nama 2 yang berbeda.", "error")
        return redirect(url_for("home"))
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Uang harus diisi dengan angka lebih dari 0.", "error")
        return redirect(url_for("home"))

    blockchain.add_transaction(sender, receiver, amount)
    if blockchain.mine():
        flash("Transaksi berhasil dikirim dan blok berhasil dibuat.", "success")
    return redirect(url_for("home"))

@app.route("/reset", methods=["POST"])
def reset():
    global blockchain
    blockchain = Blockchain()
    flash("Data blockchain dikembalikan seperti semula.", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
