#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delta PC — Roblox Script Executor for Windows
محرك سكربتات حقيقي (Lua 5.4) مع بيئة Roblox محاكاة.
"""
import sys, time, threading
import lupa

lu = lupa.LuaRuntime()

# ---------- بيئة Roblox المحاكاة ----------
class Instance:
    _internal = ("ClassName", "Name", "Parent", "children", "_attrs")
    def __init__(self, cls="Instance", name="Instance"):
        object.__setattr__(self, "ClassName", cls)
        object.__setattr__(self, "Name", name)
        object.__setattr__(self, "Parent", None)
        object.__setattr__(self, "children", {})
        object.__setattr__(self, "_attrs", {})
    def __call__(self, *a):
        print("(Instance called, ignored)")
    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        children = object.__getattribute__(self, "children")
        if item in children:
            return children[item]
        attrs = object.__getattribute__(self, "_attrs")
        if item in attrs:
            return attrs[item]
        return Instance("Value", item)
    def __setattr__(self, k, v):
        if k in Instance._internal:
            object.__setattr__(self, k, v)
        else:
            self._attrs[k] = v
    def FindFirstChild(self, n):
        return self.children.get(n)
    def IsA(self, cls):
        return self.ClassName == cls
    def WaitForChild(self, n, t=None):
        if n in self.children:
            return self.children[n]
        return Instance("Value", n)

class Part(Instance):
    def __init__(self, name="Part"):
        super().__init__("Part", name)
        self.Position = (0,0,0)
        self.Size = (4,1,4)
        self.Anchored = False
        self.BrickColor = "Bright blue"
        self.Transparency = 0.0
        self.Material = "SmoothPlastic"

class Player(Instance):
    def __init__(self, name="Player1"):
        super().__init__("Player", name)
        self.UserId = 123456
        self.Character = Instance("Model", "Character")
        self.Character.children = {"HumanoidRootPart": Part("HumanoidRootPart")}
        self.Character.HumanoidRootPart = Part("HumanoidRootPart")
        self.Character.Humanoid = Instance("Humanoid","Humanoid")
        self.Character.Humanoid.Health = 100
        self.Character.Humanoid.WalkSpeed = 16

class Players(Instance):
    def __init__(self):
        super().__init__("Players","Players")
        p1 = Player("Player1")
        p2 = Player("Guest")
        self.children = {"Player1": p1, "Guest": p2}
        self.LocalPlayer = p1
        self.PlayerList = [p1, p2]
        self.PlayerAdded = "Event"
        self.PlayerRemoving = "Event"

# بناء الـ hierarchy
game = Instance("DataModel", "game")
workspace = Instance("Workspace", "Workspace")
game.children["Workspace"] = workspace
workspace.Parent = game
game.children["Players"] = Players()
game.children["Players"].Parent = game
game.children["SoundService"] = Instance("SoundService","SoundService")
game.children["ReplicatedStorage"] = Instance("ReplicatedStorage","ReplicatedStorage")
game.children["Lighting"] = Instance("Lighting","Lighting")
game.children["Lighting"].Ambient = "0.5"
game.children["ReplicatedFirst"] = Instance("ReplicatedFirst","ReplicatedFirst")

# وضع جزء في الـ workspace
demo = Part("DemoPart")
workspace.children["DemoPart"] = demo
demo.Parent = workspace

# ---------- دوال أساسية ----------
def _print(*args):
    s = " ".join(str(a) for a in args)
    print("[Roblox] " + s, flush=True)

def _warn(*a):
    print("[warn] " + " ".join(str(x) for x in a), flush=True)

def _error(*a):
    raise RuntimeError(" ".join(str(x) for x in a))

def _wait(t=None):
    if t is None or t == 0:
        time.sleep(0)
    else:
        time.sleep(float(t))

def _tick():
    time.sleep(0.03)

def _spawn(func, *a):
    threading.Thread(target=func, args=a, daemon=True).start()

# task
class _Task:
    @staticmethod
    def wait(t=None): 
        return _wait(t)
    @staticmethod
    def delay(t, func, *a):
        def _run():
            time.sleep(float(t)); func(*a)
        threading.Thread(target=_run, daemon=True).start()
    @staticmethod
    def spawn(func, *a):
        threading.Thread(target=func, args=a, daemon=True).start()
    @staticmethod
    def defer(func, *a):
        func(*a)
    @staticmethod
    def hold(t=None):
        _wait(t)
    @staticmethod
    def repeat(t, func, *a):
        while True:
            func(*a); _wait(t)
    @staticmethod
    def resume(*a): pass
    @staticmethod
    def suspend(*a): pass
    @staticmethod
    def cancel(*a): pass
    @staticmethod
    def wait_for_child(inst, n, t=None):
        return inst.WaitForChild(n, t)

task = _Task()

# math / os / string معروضة
math = lu.eval("math")
os = lu.eval("os")
string = lu.eval("string")
table = lu.eval("table")

# ---------- حقن البيئة على جدول المتغيرات العالمية ----------
G = lu.globals()
G.game = game
G.workspace = workspace
G.Players = game.children["Players"]
G.player = game.children["Players"].LocalPlayer
G.Instance = Instance
G.Part = Part
G.Vector3 = lambda x=0,y=0,z=0: (x,y,z)
G.CFrame = "CFrame"
G.Color3 = "Color3"
G.print = _print
G.warn = _warn
G.error = _error
G.wait = _wait
G.tick = _tick
G.spawn = _spawn
G.task = task
G.math = math
G.string = string
G.table = table
G.os = os

# script object بسيط
script = Instance("LocalScript", "Script")
G["script"] = script

# ---------- واجهة tkinter ----------
import tkinter as tk
from tkinter import scrolledtext, messagebox

class App:
    def __init__(self, root):
        self.root = root
        root.title("Delta PC — Roblox Script Executor")
        root.geometry("900x640")
        root.configure(bg="#1e1e2e")

        # شريط علوي
        top = tk.Frame(root, bg="#181825"); top.pack(fill="x")
        tk.Label(top, text="Delta PC", font=("Consolas",16,"bold"),
                 fg="#89b4fa", bg="#181825").pack(side="left", padx=10, pady=6)
        tk.Label(top, text="Roblox Script Executor (PC)",
                 font=("Consolas",10), fg="#6c7086", bg="#181825").pack(side="left", padx=4)

        # أزرار
        bar = tk.Frame(root, bg="#11111b"); bar.pack(fill="x", padx=8, pady=6)
        b = lambda txt, fn, col: tk.Button(bar, text=txt, command=fn, bg=col,
            fg="white", activebackground="#45475a", relief="flat", padx=14, pady=6,
            font=("Segoe UI",10,"bold"), cursor="hand2")
        b("Execute", self.execute, "#89b4fa").pack(side="left", padx=4)
        b("Clear", self.clear, "#f38ba8").pack(side="left", padx=4)
        b("Example", self.load_example, "#a6e3a1").pack(side="left", padx=4)

        # إطار السكربت
        lbl = tk.Label(root, text="Script (Lua)", bg="#11111b", fg="#cdd6f4",
                       font=("Segoe UI",10,"bold")); lbl.pack(anchor="w", padx=10)
        self.editor = scrolledtext.ScrolledText(root, wrap="none", bg="#1e1e2e",
            fg="#cdd6f4", insertbackground="#cdd6f4", relief="flat",
            font=("Consolas",11), undo=True)
        self.editor.pack(fill="both", expand=True, padx=10, pady=(0,6))
        self.editor.insert("1.0", self.load_example_text())

        # إطار النتيجة
        lbl2 = tk.Label(root, text="Output", bg="#11111b", fg="#cdd6f4",
                        font=("Segoe UI",10,"bold")); lbl2.pack(anchor="w", padx=10)
        self.out = scrolledtext.ScrolledText(root, wrap="word", bg="#11111b",
            fg="#a6e3a1", relief="flat", font=("Consolas",10))
        self.out.pack(fill="both", expand=True, padx=10, pady=(0,8))
        self.out.configure(state="disabled")

        self._log("جاهز. ألصق سكربت واضغط Execute.")

    def load_example_text(self):
        return '''-- Delta PC | Roblox Executor
local player = game.Players.LocalPlayer

print("أهلاً يا", player.Name)
print("رقمك:", player.UserId)

-- نجري السكربت داخل الـ workspace
local part = workspace.DemoPart
print("موقع الجزء:", part.Position)

-- نغير السرعة
player.Character.Humanoid.WalkSpeed = 30
print("السرعة الجديدة:", player.Character.Humanoid.WalkSpeed)

-- حلقة مع wait
for i = 1, 3 do
    print("عدّاد:", i)
    wait(0.5)
end

print("تم ✅")
'''

    def load_example(self):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", self.load_example_text())

    def _log(self, s, err=False):
        self.out.configure(state="normal")
        self.out.insert("end", s + "\n", "err" if err else "ok")
        self.out.configure(state="disabled")
        self.out.see("end")

    def clear(self):
        self.out.configure(state="normal"); self.out.delete("1.0","end")
        self.out.configure(state="disabled")

    def execute(self):
        self.clear()
        code = self.editor.get("1.0", "end-1c")
        self._log("▶ تشغيل السكربت...")
        try:
            lu.execute(code)
            self._log("✔ انتهى بنجاح.")
        except Exception as e:
            self._log("✖ خطأ: " + str(e), err=True)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
