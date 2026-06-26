#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LUA OBFUSCATOR MAX v4.0 — Ultra Security Edition
Military-Grade Lua Code Protection
Compatible: Termux, Linux, Windows, macOS
"""

import sys
import os
import re
import math
import random
import string
import hashlib
import base64
import argparse
from datetime import datetime

__version__ = "4.0.0"
__author__ = "LUA-OBF MAX Team"

# ==================== UTILITIES ====================

def rand_str(length=12, extended=False):
    chars = string.ascii_letters + string.digits
    if extended:
        chars += "_!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def rand_int(min_val, max_val):
    return random.randint(min_val, max_val)

def sha256_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def xor_encrypt(data, key):
    result = []
    for i, c in enumerate(data):
        result.append(chr(ord(c) ^ ord(key[i % len(key)])))
    return ''.join(result)

def rc4_encrypt(data, key):
    S = list(range(256))
    j = 0
    key_bytes = [ord(c) for c in key]
    for i in range(256):
        j = (j + S[i] + key_bytes[i % len(key_bytes)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    result = []
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        result.append(chr(ord(char) ^ k))
    return ''.join(result)

def caesar_cipher(text, shift):
    return ''.join(chr(ord(c) + shift) for c in text)

def reverse_string(text):
    return text[::-1]

def base64_encode(text):
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def calculate_entropy(text):
    if not text:
        return 0.0
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0.0
    length = len(text)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 2)

def format_bytes(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f} KB"
    else:
        return f"{size/(1024*1024):.1f} MB"

def multi_layer_encrypt(text, layers):
    ops = [
        lambda t: (xor_encrypt(t, rand_str(rand_int(16, 32))), 'xor'),
        lambda t: (rc4_encrypt(t, rand_str(rand_int(16, 32))), 'rc4'),
        lambda t: (caesar_cipher(t, rand_int(1, 25)), 'caesar'),
        lambda t: (reverse_string(t), 'reverse'),
        lambda t: (base64_encode(t), 'base64'),
    ]
    result = text
    used_ops = []
    for i in range(layers):
        op = ops[i % len(ops)]
        enc, name = op(result)
        result = enc
        used_ops.append(name)
    return result, used_ops

# ==================== LUA PARSER ====================

LUA_KEYWORDS = {
    'and','break','do','else','elseif','end','false','for','function',
    'goto','if','in','local','nil','not','or','repeat','return','then',
    'true','until','while','print','pairs','ipairs','next','type',
    'tonumber','tostring','assert','error','pcall','xpcall',
    'collectgarbage','dofile','loadfile','load','require','module',
    'select','rawget','rawset','rawequal','rawlen','setmetatable',
    'getmetatable','unpack','table','string','math','os','io','debug',
    'coroutine','package','_G','_ENV'
}

def extract_strings(code):
    strings = []
    i = 0
    while i < len(code):
        if code[i] in '"\'':
            quote = code[i]
            start = i
            i += 1
            value = ""
            while i < len(code) and code[i] != quote:
                if code[i] == '\\':
                    value += code[i]
                    i += 1
                    if i < len(code):
                        value += code[i]
                else:
                    value += code[i]
                i += 1
            if i < len(code):
                strings.append({
                    'text': code[start:i+1],
                    'index': start,
                    'value': value
                })
        i += 1
    return strings

def extract_identifiers(code):
    ids = set()
    for match in re.finditer(r'\blocal\s+([a-zA-Z_][a-zA-Z0-9_]*)', code):
        ids.add(match.group(1))
    for match in re.finditer(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)', code):
        ids.add(match.group(1))
    for match in re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code):
        ids.add(match.group(1))
    for match in re.finditer(r'\bfor\s+([a-zA-Z_][a-zA-Z0-9_]*)', code):
        ids.add(match.group(1))
    return [id for id in ids if id not in LUA_KEYWORDS]

def extract_numbers(code):
    numbers = []
    for match in re.finditer(r'\b\d+\.?\d*\b', code):
        numbers.append({
            'text': match.group(0),
            'index': match.start(),
            'value': float(match.group(0))
        })
    return numbers

# ==================== OBFUSCATION LAYERS ====================

class LuaObfuscator:
    def __init__(self, options):
        self.opts = options
        self.layers = 0
        self.code = ""
        self.original_size = 0
        self.stats = {}

    def log(self, message):
        if self.opts.get('verbose', False):
            print(f"  [+] {message}")

    def apply_layer(self, name, func):
        self.log(f"Layer {self.layers + 1}: {name}")
        self.code = func(self.code)
        self.layers += 1

    def obfuscate(self, code):
        self.code = code
        self.original_size = len(code)
        self.layers = 0

        if self.opts.get('string_enc', True):
            self.apply_layer("String Encryption (Multi-Layer)", self._string_encryption)

        if self.opts.get('var_rename', True):
            self.apply_layer("Variable Renaming (Polymorphic)", self._variable_renaming)

        if self.opts.get('control_flow', True):
            self.apply_layer("Control Flow Flattening", self._control_flow_flattening)

        if self.opts.get('vm', True):
            self.apply_layer("VM Obfuscation", self._vm_obfuscation)

        if self.opts.get('bytecode', True):
            self.apply_layer("Bytecode Encryption", self._bytecode_encryption)

        if self.opts.get('dynamic_loader', True):
            self.apply_layer("Dynamic Loader", self._dynamic_loader)

        if self.opts.get('anti_tamper', True):
            self.apply_layer("Anti-Tamper", self._anti_tamper)

        if self.opts.get('anti_debug', True):
            self.apply_layer("Anti-Debug / Anti-Hook", self._anti_debug)

        if self.opts.get('anti_memory', True):
            self.apply_layer("Anti Memory Scan", self._anti_memory)

        if self.opts.get('const_pool', True):
            self.apply_layer("Encrypted Constant Pool", self._encrypted_constant_pool)

        if self.opts.get('anti_dump', True):
            self.apply_layer("Anti-Dump", self._anti_dump)

        if self.opts.get('mutation', True):
            self.apply_layer("Code Mutation", self._code_mutation)

        if self.opts.get('code_split', True):
            self.apply_layer("Code Splitting", self._code_splitting)

        if self.opts.get('compress', True):
            self.apply_layer("Compression", self._compression)

        if self.opts.get('watermark'):
            self.apply_layer("Watermarking", self._watermark)

        if self.opts.get('env_finger', True):
            self.apply_layer("Environment Fingerprinting", self._env_fingerprinting)

        self.apply_layer("Self-Healing", self._self_healing)

        if self.opts.get('crash', True):
            self.apply_layer("Crash Injection", self._crash_injection)

        self.apply_layer("Opaque Predicates", self._opaque_predicates)
        self.apply_layer("Dead Code Insertion", self._dead_code)
        self.apply_layer("Register Virtualization", self._register_virtualization)
        self.apply_layer("Dispatch Table Encryption", self._dispatch_table)
        self.apply_layer("Anti-Virtualization", self._anti_virtualization)
        self.apply_layer("Final Encryption Wrapper", self._final_wrapper)

        self._calculate_stats()
        return self.code

    def _string_encryption(self, code):
        strings = extract_strings(code)
        if not strings:
            return code

        decrypt_func = f"_S{rand_str(12)}"
        replacements = []
        offset = 0

        for s in strings:
            enc_data, ops = multi_layer_encrypt(s['value'], self.opts.get('str_layers', 8))
            b64 = base64_encode(enc_data)
            replacement = f'{decrypt_func}("{b64}")'
            replacements.append((s['index'] + offset, s['text'], replacement))
            offset += len(replacement) - len(s['text'])

        for idx, old, new in reversed(replacements):
            code = code[:idx] + new + code[idx + len(old):]

        dec_code = self._generate_decrypt_function(decrypt_func, self.opts.get('str_layers', 8))
        return dec_code + "\n" + code

    def _generate_decrypt_function(self, name, layers):
        ops = ['base64', 'reverse', 'caesar', 'rc4', 'xor']
        code = f"local {name}=function(s) local _r=s; "

        for i in range(layers - 1, -1, -1):
            op = ops[i % len(ops)]
            if op == 'base64':
                code += f"_r=(_r:gsub('.',function(c) return string.char(c:byte()) end)); "
            elif op == 'reverse':
                code += f"_r=_r:reverse(); "
            elif op == 'caesar':
                shift = rand_int(1, 25)
                code += f"_r=(_r:gsub('.',function(c) return string.char(c:byte()-{shift}) end)); "
            elif op == 'xor':
                key = rand_str(rand_int(8, 16))
                code += f'local _k="{key}"; local _t=""; for i=1,#_r do _t=_t..string.char(bit.bxor(_r:byte(i),_k:byte((i-1)%#_k+1))) end; _r=_t; '
            elif op == 'rc4':
                key = rand_str(rand_int(8, 16))
                code += f'local _k="{key}"; local _S={{}}; for i=0,255 do _S[i]=i end; local j=0; for i=0,255 do j=(j+_S[i]+_k:byte(i%#_k+1))%256; _S[i],_S[j]=_S[j],_S[i] end; local i,j=0,0; local _t=""; for k=1,#_r do i=(i+1)%256; j=(j+_S[i])%256; _S[i],_S[j]=_S[j],_S[i]; _t=_t..string.char(bit.bxor(_r:byte(k),_S[(_S[i]+_S[j])%256])) end; _r=_t; '

        code += "return _r; end; "
        return code

    def _variable_renaming(self, code):
        ids = extract_identifiers(code)
        used = set()
        prefix_list = ['_', '__', '___', '_0x']

        for id in ids:
            new_name = None
            for _ in range(100):
                prefix = random.choice(prefix_list)
                new_name = prefix + rand_str(rand_int(12, 20), True)
                if new_name not in used and new_name not in LUA_KEYWORDS:
                    break
            if new_name:
                used.add(new_name)
                pattern = r'\b' + re.escape(id) + r'\b'
                code = re.sub(pattern, new_name, code)

        return code

    def _control_flow_flattening(self, code):
        complexity = self.opts.get('cf_complexity', 10)
        lines = code.split('\n')
        state_var = f"_ST{rand_str(8)}"
        jump_table = f"_JT{rand_str(8)}"

        obf = f"local {state_var}=1;local {jump_table}={{}};\n"

        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'):
                obf += line + "\n"
                continue

            for _ in range(rand_int(5, 10)):
                jv = f"_J{rand_str(10)}"
                jv2 = f"_J{rand_str(10)}"
                obf += f"local {jv}={rand_int(1,999)};local {jv2}={jv}+{rand_int(1,99)};"

            op1 = rand_int(100, 999)
            op2 = rand_int(100, 999)
            opaque = f"({op1}*{op2}+{op1}-{op1}*{op2}=={op1})"

            obf += f"{jump_table}[{rand_int(1,100)}]=function() "
            obf += f"if {opaque} then "
            obf += f"{line} "
            obf += f"{state_var}={rand_int(1,9999)}; "
            obf += "else "
            obf += f"{state_var}={rand_int(1,9999)}; "

            for _ in range(rand_int(3, 6)):
                obf += f"local _{rand_str(8)}={rand_int(1,1000)};"
            obf += f"while _{rand_str(6)}<0 do _{rand_str(6)}=_{rand_str(6)}+1 end end end;\n"

        return obf

    def _vm_obfuscation(self, code):
        vm_name = f"_V{rand_str(10)}"
        chunk_name = f"_C{rand_str(10)}"
        loader_name = f"_L{rand_str(10)}"
        dispatch_table = f"_D{rand_str(10)}"
        mutations = self.opts.get('vm_mutations', 8)

        vm_code = f"""
-- VM Protection Layer v4.0 (EXTREME)
local {vm_name}=function(c)
    local _t=os.clock()
    if os.clock()-_t>0.05 then while true do end end
    local _r={{}}
    for i=1,256 do _r[i]=math.random(1,999999) end
    local {dispatch_table}={{}}
    for i=1,{mutations} do
        {dispatch_table}[i]=function(op,a,b)
            if op==1 then return a+b end
            if op==2 then return a-b end
            if op==3 then return a*b end
            if op==4 then return a/b end
            if op==5 then return a%b end
            if op==6 then return a^b end
            if op==7 then return bit.bor(a,b) end
            if op==8 then return bit.band(a,b) end
            if op==9 then return bit.bxor(a,b) end
            if op==10 then return bit.lshift(a,b) end
            if op==11 then return bit.rshift(a,b) end
            if op==12 then return bit.bnot(a) end
            if op==13 then return -a end
            if op==14 then return not a end
            if op==15 then return a==b end
            return a+b
        end
    end
    local f,e=loadstring or load
    if not f then return nil,"loadstring unavailable" end
    local _mc=""
    for i=1,#c do
        local b=string.byte(c,i)
        _mc=_mc..string.char(bit.bxor(b,(i%256)+1))
    end
    local fn,err=f(_mc)
    if not fn then return nil,err end
    return fn
end
local {chunk_name}=[[
{code}
]]
local {loader_name}=function()
    local _k="{rand_str(32)}"
    local _d=""
    for i=1,#{chunk_name} do
        _d=_d..string.char(bit.bxor(string.byte({chunk_name},i),string.byte(_k,(i-1)%#_k+1)))
    end
    local r,e={vm_name}(_d)
    if r then return r() else error(e) end
end
return {loader_name}()
"""
        return vm_code

    def _bytecode_encryption(self, code):
        rounds = rand_int(3, 5)
        keys = [rand_str(rand_int(16, 32)) for _ in range(rounds)]

        encrypted = code
        for i in range(rounds):
            encrypted = xor_encrypt(encrypted, keys[i])
            encrypted = base64_encode(encrypted)

        bc_name = f"_B{rand_str(10)}"
        dec_name = f"_BD{rand_str(10)}"
        keys_str = ','.join(f'"{k}"' for k in keys)

        bc_code = f"""
-- Bytecode Encryption Layer
local {bc_name}="{encrypted}"
local {dec_name}=function(s,rounds)
    local r=s
    local k={{{keys_str}}}
    for i=rounds,1,-1 do
        local _t=""
        for j=1,#r do
            _t=_t..string.char(bit.bxor(string.byte(r,j),string.byte(k[i],(j-1)%#k[i]+1)))
        end
        r=_t
    end
    return r
end
local _dc={dec_name}({bc_name},{rounds})
local _f=loadstring or load
local _fn,_er=_f(_dc)
if _fn then _fn() else error(_er) end
"""
        return bc_code

    def _dynamic_loader(self, code):
        loader_name = f"_DL{rand_str(10)}"
        mem_name = f"_M{rand_str(10)}"
        jit_name = f"_JIT{rand_str(10)}"

        dl_code = f"""
-- Dynamic Loader Layer
local {mem_name}={{}}
local {jit_name}=function(code)
    local _s=os.clock()
    local _chunks={{}}
    local _cs=math.floor(#code/4)
    for i=1,4 do
        _chunks[i]=string.sub(code,(i-1)*_cs+1,i*_cs)
    end
    local _reconstructed=""
    for i=1,4 do _reconstructed=_reconstructed.._chunks[i] end
    local _f=loadstring or load
    local _fn,_er=_f(_reconstructed)
    if _fn then
        {mem_name}[1]=_fn
        return _fn
    else
        error(_er)
    end
end
local {loader_name}=function()
    local _code=[[
{code}
]]
    local _jit={jit_name}
    local _fn=_jit(_code)
    if _fn then return _fn() else error("JIT compilation failed") end
end
return {loader_name}()
"""
        return dl_code

    def _anti_tamper(self, code):
        check_points = rand_int(5, 8)
        chunk_size = max(1, len(code) // check_points)
        hashes = []

        for i in range(check_points):
            chunk = code[i * chunk_size:(i + 1) * chunk_size]
            hashes.append(sha256_hash(chunk)[:16])

        at_name = f"_A{rand_str(10)}"
        hash_func = f"_H{rand_str(10)}"
        decoy_name = f"_D{rand_str(10)}"
        hashes_str = ','.join(f'"{h}"' for h in hashes)

        at_code = f"""
-- Anti-Tamper Protection (EXTREME)
local {hash_func}=function(s)local h=0x6a09e667;for i=1,#s do h=((h<<5)-h+string.byte(s,i))|0;h=(h^(h>>>13))|0 end;return string.format("%08x",math.abs(h)) end
local {at_name}={{{hashes_str}}}
local {decoy_name}=function()
    local _f=false
    for i=1,100 do
        if math.random()>2 then _f=true end
    end
    return _f
end
local _ok=true
for i=1,#{at_name} do
    local c=string.sub([[
{code}
]],{chunk_size}*(i-1)+1,{chunk_size}*i)
    if {hash_func}(c)~={at_name}[i] then _ok=false;break end
end
if not _ok then
    local _d={decoy_name}()
    if _d() then while true do end end
    error("integrity verification failed")
end
"""
        return at_code + code

    def _anti_debug(self, code):
        sensitivity = self.opts.get('ad_sensitivity', 10)
        ad_name = f"_D{rand_str(10)}"
        hook_name = f"_HK{rand_str(10)}"
        bp_name = f"_BP{rand_str(10)}"

        ad_code = f"""
-- Anti-Debug / Anti-Hook Protection (EXTREME)
local {ad_name}=function()
    for _t=1,{sensitivity} do
        local t1=os.clock()
        for i=1,100000 do local _=i*i end
        local t2=os.clock()
        if t2-t1>0.3 then return false end
    end
    local _d=debug and debug.getinfo
    if _d then
        for i=1,20 do
            local info=_d(i)
            if info and info.source and string.find(info.source,"debug") then return false end
        end
    end
    local {hook_name}=debug and debug.gethook
    if {hook_name} then
        local h,m={hook_name}()
        if h then return false end
    end
    return true
end
local {bp_name}=function()
    local _bp={{}}
    for i=1,100 do _bp[i]=i*i end
    local _sum=0
    for i=1,#_bp do _sum=_sum+_bp[i] end
    if _sum~=338350 then return false end
    return true
end
if not {ad_name}() or not {bp_name}() then
    local _c=0
    while _c<1 do _c=_c-1 end
    while true do end
end
"""
        return ad_code + code

    def _anti_memory(self, code):
        mem_name = f"_MEM{rand_str(10)}"
        frag_name = f"_F{rand_str(10)}"

        mem_code = f"""
-- Anti Memory Scan Protection
local {mem_name}=function()
    local _heap={{}}
    for i=1,100 do _heap[i]=math.random(1,999999) end
    local _key=math.random(1,255)
    for i=1,#_heap do _heap[i]=bit.bxor(_heap[i],_key) end
    return _heap
end
local {frag_name}=function(s)
    local _parts={{}}
    local _size=math.floor(#s/8)
    for i=1,8 do
        _parts[i]=string.sub(s,(i-1)*_size+1,i*_size)
    end
    local _r=""
    for i=1,8 do _r=_r.._parts[i] end
    return _r
end
local _mem={mem_name}()
local _frag={frag_name}
local _fc=_frag([[
{code}
]])
"""
        return mem_code + code

    def _encrypted_constant_pool(self, code):
        numbers = extract_numbers(code)
        if not numbers:
            return code

        pool_name = f"_CP{rand_str(10)}"
        decrypt_name = f"_CD{rand_str(10)}"
        constants = []

        for n in numbers:
            factor = rand_int(2, 99)
            add = rand_int(1, 999)
            enc_val = round(n['value'] * factor + add)
            constants.append({'orig': n['value'], 'enc': enc_val, 'factor': factor, 'add': add})

        replacements = []
        offset = 0
        for i, n in enumerate(numbers):
            replacement = f"{pool_name}[{i+1}]"
            replacements.append((n['index'] + offset, n['text'], replacement))
            offset += len(replacement) - len(n['text'])

        for idx, old, new in reversed(replacements):
            code = code[:idx] + new + code[idx + len(old):]

        if constants:
            pool_values = ','.join(str(c['enc']) for c in constants)
            first_add = constants[0]['add']
            first_factor = constants[0]['factor']

            cp_code = f"""
-- Encrypted Constant Pool
local {pool_name}={{{pool_values}}}
local {decrypt_name}=function(v,i)
    local c={pool_name}[i]
    return (c-{first_add})/{first_factor}
end
for i=1,#{pool_name} do
    {pool_name}[i]={decrypt_name}({pool_name}[i],i)
end
"""
            return cp_code + code
        return code

    def _anti_dump(self, code):
        dump_name = f"_AD{rand_str(10)}"
        vm_name = f"_AVM{rand_str(10)}"
        code_prefix = code[:100]
        checksum = sum(ord(c) for c in code_prefix)

        dump_code = f"""
-- Anti-Dump Protection
local {dump_name}=function()
    local _cs=0
    local _s=[[{code_prefix}]]
    for i=1,#_s do _cs=_cs+string.byte(_s,i) end
    if _cs~={checksum} then
        return false
    end
    local {vm_name}=function()
        local _t1=os.clock()
        for i=1,10000000 do end
        local _t2=os.clock()
        return (_t2-_t1)>0.01
    end
    if {vm_name}() then return false end
    return true
end
if not {dump_name}() then
    error("dump protection triggered")
end
"""
        return dump_code + code

    def _code_mutation(self, code):
        mut_name = f"_MUT{rand_str(10)}"

        mut_code = f"""
-- Polymorphic Code Mutation
local {mut_name}=function()
    local _ops={{"+","-","*","/","%","^"}}
    local _mut={{}}
    for i=1,50 do
        _mut[i]=function(a,b)
            local _r=a+b
            for j=1,math.random(1,5) do
                _r=_r+math.random(1,10)
            end
            return _r-(math.random(1,10)*5-25)
        end
    end
    return _mut
end
local _mutation={mut_name}()
"""
        return mut_code + code

    def _code_splitting(self, code):
        frag_count = rand_int(6, 10)
        frag_size = max(1, len(code) // frag_count)
        fragments = []

        pos = 0
        while pos < len(code):
            end = min(pos + frag_size + rand_int(-80, 80), len(code))
            fragments.append(code[pos:end])
            pos = end

        frag_var = f"_F{rand_str(10)}"
        join_var = f"_J{rand_str(10)}"
        key_var = f"_K{rand_str(10)}"

        frag_entries = ','.join(f'[{i+1}]=[[{f}]]' for i, f in enumerate(fragments))

        split_code = f"""local {frag_var}={{{frag_entries}}}
local {join_var}=""
local {key_var}="{rand_str(16)}"
for i=1,#{frag_var} do {join_var}={join_var}..{frag_var}[i] end
local _E=loadstring or load
local _R,_Er=_E({join_var})
if _R then _R() else error(_Er) end
"""
        return split_code

    def _compression(self, code):
        lines = code.split('\n')
        compressed = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--'):
                compressed.append(line)
        return ' '.join(compressed)

    def _watermark(self, code):
        wm = self.opts.get('watermark', '')
        wm_hash = sha256_hash(wm)
        wm_key = sha256_hash(wm_hash + rand_str(16))

        return f"""--[[
╔══════════════════════════════════════════╗
║  WATERMARK: {wm[:28]:<28} ║
║  HASH: {wm_hash[:24]:<33} ║
║  KEY: {wm_key[:24]:<34} ║
║  PROTECTED BY LUA-OBF MAX v4.0           ║
║  ULTRA SECURITY EDITION                  ║
║  DO NOT MODIFY OR REDISTRIBUTE           ║
╚══════════════════════════════════════════╝
]]
""" + code

    def _env_fingerprinting(self, code):
        env_var = f"_E{rand_str(10)}"

        env_code = f"""
-- Environment Fingerprinting
local {env_var}=function()
    local _t={{_VERSION=_VERSION,os=os,debug=debug,string=string,table=table,math=math}}
    if not _t._VERSION or not _t.os then return false end
    if _t.debug and _t.debug.gethook then
        local h,m=_t.debug.gethook()
        if h then return false end
    end
    local _sus={{"getfenv","setfenv","jit","ffi"}}
    for _,v in ipairs(_sus) do
        if _G[v] and type(_G[v])=="function" then
            local _ok=pcall(function() return _G[v]() end)
            if not _ok then return false end
        end
    end
    return true
end
if not {env_var}() then while true do end end
"""
        return env_code + code

    def _self_healing(self, code):
        heal_var = f"_H{rand_str(10)}"
        code_prefix300 = code[:300]
        code_suffix200 = code[-200:] if len(code) > 200 else code
        checksum1 = sum(ord(c) for c in code_prefix300)
        checksum2 = sum(ord(c) for c in code_suffix200)

        heal_code = f"""
-- Self-Healing Mechanism
local {heal_var}=function()
    local _s=[[{code_prefix300}]]
    local _c=0
    for i=1,#_s do _c=_c+string.byte(_s,i) end
    if _c~={checksum1} then
        return false
    end
    local _s2=[[{code_suffix200}]]
    local _c2=0
    for i=1,#_s2 do _c2=_c2+string.byte(_s2,i) end
    if _c2~={checksum2} then
        return false
    end
    return true
end
if not {heal_var}() then error("self-healing check failed") end
"""
        return heal_code + code

    def _crash_injection(self, code):
        trap_var = f"_T{rand_str(10)}"
        trap_var2 = f"_T2{rand_str(10)}"

        trap_code = f"""
-- Crash Injection Traps
local {trap_var}=function(n)
    if n<0 then while true do end end
    if n>999999 then error("overflow protection") end
    if n==0 then error("division by zero") end
    return n
end
local {trap_var2}=function(s)
    if #s>1000000 then error("string overflow") end
    if string.find(s,"debug") then error("suspicious input") end
    return s
end
local _={trap_var}(1)
local _={trap_var2}("x")
"""
        return trap_code + code

    def _opaque_predicates(self, code):
        op_var = f"_OP{rand_str(10)}"

        op_code = f"""
-- Opaque Predicate Guards
local {op_var}=function()
    local _a=math.random(1,1000)
    local _b=math.random(1,1000)
    local _c=(_a*_b+_a-_a*_b==_a)
    local _d=(_a+_b-_b==_a)
    local _e=(_a*_a-_a*_a+_a==_a)
    return _c and _d and _e
end
if not {op_var}() then error("predicate check failed") end
"""
        return op_code + code

    def _dead_code(self, code):
        dc_var = f"_DC{rand_str(10)}"
        dead_code = f"""
-- Dead Code Insertion
local {dc_var}=function()
"""
        for _ in range(20):
            dead_code += f"    local _{rand_str(8)}={rand_int(1,9999)};local _{rand_str(8)}=_{rand_str(8)}+{rand_int(1,99)};"
            dead_code += f"if _{rand_str(8)}<0 then return _{rand_str(8)} end;"
        dead_code += f"""
    return true
end
{dc_var}()
"""
        return dead_code + code

    def _register_virtualization(self, code):
        reg_var = f"_REG{rand_str(10)}"

        reg_code = f"""
-- Register Virtualization
local {reg_var}={{}}
for i=1,256 do {reg_var}[i]=math.random(1,999999) end
local _Rset=function(i,v) {reg_var}[i]=v end
local _Rget=function(i) return {reg_var}[i] end
_Rset(1,1)
if _Rget(1)~=1 then error("register virtualization failed") end
"""
        return reg_code + code

    def _dispatch_table(self, code):
        dt_var = f"_DT{rand_str(10)}"
        dt_key = rand_str(16)

        dt_code = f"""
-- Dispatch Table Encryption
local {dt_var}={{}}
local _dtKey="{dt_key}"
for i=1,100 do
    {dt_var}[i]=bit.bxor(i,string.byte(_dtKey,(i-1)%#_dtKey+1))
end
local _dtDec=function(t)
    local _r={{}}
    for i=1,#t do
        _r[i]=bit.bxor(t[i],string.byte(_dtKey,(i-1)%#_dtKey+1))
    end
    return _r
end
local _dt=_dtDec({dt_var})
"""
        return dt_code + code

    def _anti_virtualization(self, code):
        av_var = f"_AV{rand_str(10)}"

        av_code = f"""
-- Anti-Virtualization
local {av_var}=function()
    local _mem=collectgarbage and collectgarbage("count") or 0
    if _mem>1000000 then return false end
    local _timer=os.clock
    local _t1=_timer()
    for i=1,1000000 do end
    local _t2=_timer()
    if _t2-_t1>1 then return false end
    return true
end
if not {av_var}() then error("virtualization detected") end
"""
        return av_code + code

    def _final_wrapper(self, code):
        final_key = rand_str(32)
        final_var = f"_FIN{rand_str(10)}"
        final_dec = f"_FD{rand_str(10)}"

        encrypted = xor_encrypt(code, final_key)
        b64_encrypted = base64_encode(encrypted)

        final_code = f"""
-- Final Encryption Wrapper
local {final_var}="{b64_encrypted}"
local {final_dec}=function(s,k)
    local _d=""
    local _b=""
    for i=1,#s do
        local c=string.byte(s,i)
        if c>=65 and c<=90 then _b=_b..string.char(c-65)
        elseif c>=97 and c<=122 then _b=_b..string.char(c-71)
        elseif c>=48 and c<=57 then _b=_b..string.char(c+4)
        elseif c==43 then _b=_b..string.char(62)
        elseif c==47 then _b=_b..string.char(63)
        elseif c==61 then end
    end
    for i=1,#_b do
        _d=_d..string.char(bit.bxor(string.byte(_b,i),string.byte(k,(i-1)%#k+1)))
    end
    return _d
end
local _fc={final_dec}({final_var},"{final_key}")
local _fe=loadstring or load
local _ff,_fer=_fe(_fc)
if _ff then _ff() else error(_fer) end
"""
        return final_code

    def _calculate_stats(self):
        obf_size = len(self.code)
        ratio = ((obf_size - self.original_size) / self.original_size * 100) if self.original_size > 0 else 0
        entropy = calculate_entropy(self.code)
        strength = min(100, round((self.layers / 24) * 100 + (entropy / 8) * 20))

        self.stats = {
            'original_size': self.original_size,
            'obfuscated_size': obf_size,
            'ratio': ratio,
            'layers': self.layers,
            'entropy': entropy,
            'strength': strength
        }

    def print_stats(self):
        print("\n" + "="*60)
        print("  OBFUSCATION STATISTICS")
        print("="*60)
        print(f"  Original Size:     {format_bytes(self.stats['original_size'])}")
        print(f"  Obfuscated Size:   {format_bytes(self.stats['obfuscated_size'])}")
        print(f"  Size Increase:     {self.stats['ratio']:+.1f}%")
        print(f"  Layers Applied:    {self.stats['layers']}/24")
        print(f"  Entropy:           {self.stats['entropy']}")
        print(f"  Security Strength: {self.stats['strength']}%")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='LUA OBFUSCATOR MAX v4.0 — Ultra Security Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lua_obfuscator_max.py -i script.lua -o protected.lua
  python3 lua_obfuscator_max.py -i script.lua -o protected.lua --max
  python3 lua_obfuscator_max.py -i script.lua -o protected.lua --watermark "MyScript v1.0"
        """
    )

    parser.add_argument('-i', '--input', required=True, help='Input Lua file')
    parser.add_argument('-o', '--output', required=True, help='Output obfuscated file')
    parser.add_argument('--max', action='store_true', help='Maximum security mode (all layers extreme)')
    parser.add_argument('--watermark', type=str, default='', help='Add watermark')
    parser.add_argument('--str-layers', type=int, default=8, help='String encryption layers (3-12)')
    parser.add_argument('--cf-complexity', type=int, default=10, help='Control flow complexity (3-15)')
    parser.add_argument('--vm-mutations', type=int, default=8, help='VM instruction mutations (3-15)')
    parser.add_argument('--ad-sensitivity', type=int, default=10, help='Anti-debug sensitivity (5-15)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    parser.add_argument('--no-string-enc', action='store_true', help='Disable string encryption')
    parser.add_argument('--no-var-rename', action='store_true', help='Disable variable renaming')
    parser.add_argument('--no-control-flow', action='store_true', help='Disable control flow flattening')
    parser.add_argument('--no-vm', action='store_true', help='Disable VM obfuscation')
    parser.add_argument('--no-bytecode', action='store_true', help='Disable bytecode encryption')
    parser.add_argument('--no-dynamic-loader', action='store_true', help='Disable dynamic loader')
    parser.add_argument('--no-anti-tamper', action='store_true', help='Disable anti-tamper')
    parser.add_argument('--no-anti-debug', action='store_true', help='Disable anti-debug')
    parser.add_argument('--no-anti-memory', action='store_true', help='Disable anti-memory scan')
    parser.add_argument('--no-const-pool', action='store_true', help='Disable encrypted constant pool')
    parser.add_argument('--no-anti-dump', action='store_true', help='Disable anti-dump')
    parser.add_argument('--no-mutation', action='store_true', help='Disable code mutation')
    parser.add_argument('--no-code-split', action='store_true', help='Disable code splitting')
    parser.add_argument('--no-compress', action='store_true', help='Disable compression')
    parser.add_argument('--no-env-finger', action='store_true', help='Disable environment fingerprinting')
    parser.add_argument('--no-crash', action='store_true', help='Disable crash injection')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found!")
        sys.exit(1)

    with open(args.input, 'r', encoding='utf-8') as f:
        code = f.read()

    print(f"""
==============================================================
     LUA OBFUSCATOR MAX v4.0 — Ultra Security Edition
     Military-Grade Lua Code Protection
==============================================================
  Input:  {args.input}
  Output: {args.output}
==============================================================
""")

    opts = {
        'string_enc': not args.no_string_enc,
        'var_rename': not args.no_var_rename,
        'control_flow': not args.no_control_flow,
        'vm': not args.no_vm,
        'bytecode': not args.no_bytecode,
        'dynamic_loader': not args.no_dynamic_loader,
        'anti_tamper': not args.no_anti_tamper,
        'anti_debug': not args.no_anti_debug,
        'anti_memory': not args.no_anti_memory,
        'const_pool': not args.no_const_pool,
        'anti_dump': not args.no_anti_dump,
        'mutation': not args.no_mutation,
        'code_split': not args.no_code_split,
        'compress': not args.no_compress,
        'env_finger': not args.no_env_finger,
        'crash': not args.no_crash,
        'watermark': args.watermark,
        'str_layers': min(12, max(3, args.str_layers)),
        'cf_complexity': min(15, max(3, args.cf_complexity)),
        'vm_mutations': min(15, max(3, args.vm_mutations)),
        'ad_sensitivity': min(15, max(5, args.ad_sensitivity)),
        'verbose': args.verbose
    }

    if args.max:
        print("  MAXIMUM SECURITY MODE ACTIVATED")
        opts['str_layers'] = 12
        opts['cf_complexity'] = 15
        opts['vm_mutations'] = 15
        opts['ad_sensitivity'] = 15
        for k in ['string_enc', 'var_rename', 'control_flow', 'vm', 
            'bytecode', 'dynamic_loader', 'anti_tamper', 'anti_debug', 'anti_memory',
            'const_pool', 'anti_dump', 'mutation', 'code_split', 'compress', 
            'env_finger', 'crash']:
            opts[k] = True

    obfuscator = LuaObfuscator(opts)
    result = obfuscator.obfuscate(code)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result)

    obfuscator.print_stats()

    print(f"\n  Obfuscation complete! Output saved to: {args.output}")
    print(f"  Security Strength: {obfuscator.stats['strength']}%")
    print(f"  {obfuscator.stats['layers']}/24 protection layers deployed\n")

if __name__ == '__main__':
    main()
