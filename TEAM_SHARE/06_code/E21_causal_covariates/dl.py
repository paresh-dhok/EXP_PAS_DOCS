import os,time,requests,struct,zlib
def get(url,dst,tries=8):
    """download whole file with resume + retries"""
    for a in range(tries):
        try:
            pos=os.path.getsize(dst) if os.path.exists(dst) else 0
            h={"Range":f"bytes={pos}-"} if pos else {}
            with requests.get(url,headers=h,stream=True,timeout=120) as r:
                if r.status_code==416: return dst
                r.raise_for_status()
                with open(dst,"ab" if pos else "wb") as o:
                    for ch in r.iter_content(2**20): o.write(ch)
            return dst
        except Exception as e: print(" retry",a,os.path.basename(dst),e,flush=True); time.sleep(5*(a+1))
    raise RuntimeError("download failed "+url)
def rng(url,start,end,tries=8):
    for a in range(tries):
        try:
            r=requests.get(url,headers={"Range":f"bytes={start}-{end}"},timeout=180); r.raise_for_status()
            if len(r.content)==end-start+1: return r.content
            raise IOError(f"short {len(r.content)}")
        except Exception as e: print(" retry range",a,e,flush=True); time.sleep(5*(a+1))
    raise RuntimeError("range failed")
def zip_member(url,info,dst,chunk=32*2**20):
    """extract one deflated member of a remote zip via range requests (resumable chunks)"""
    hdr=rng(url,info.header_offset,info.header_offset+29)
    n,e=struct.unpack("<HH",hdr[26:30]); start=info.header_offset+30+n+e; end=start+info.compress_size-1
    d=zlib.decompressobj(-15) if info.compress_type==8 else None
    with open(dst,"wb") as o:
        p=start
        while p<=end:
            b=rng(url,p,min(p+chunk-1,end)); o.write(d.decompress(b) if d else b); p+=len(b)
        if d: o.write(d.flush())
    return dst
