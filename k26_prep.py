import csv, os, re, urllib.request, concurrent.futures as cf
SRC = r"C:\Users\sanno\Downloads\contacts (1).csv"
OUT = r"C:\Users\sanno\Downloads\K26"
PH = os.path.join(OUT, "photos")
os.makedirs(PH, exist_ok=True)
rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
recs = []
for i, r in enumerate(rows):
    g = lambda k: (r.get(k) or "").strip()
    full = " ".join(x for x in [g("Name Prefix"), g("First Name"), g("Middle Name"), g("Last Name"), g("Name Suffix")] if x).strip()
    first = g("First Name")
    last = " ".join(x for x in [g("Middle Name"), g("Last Name")] if x).strip()
    phone = g("Phone 1 - Value").split(":::")[0].strip()
    email = g("E-mail 1 - Value").split(":::")[0].strip()
    photo = g("Photo")
    safe = re.sub(r"[^A-Za-z0-9]+", "_", full).strip("_")[:60] or f"contact_{i+1}"
    fn = f"{i+1:03d}_{safe}.jpg" if photo else ""
    recs.append(dict(idx=i+1, full=full, first=first, last=last, phone=phone, email=email,
                     company=g("Organization Name"), title=g("Organization Title"), photo=photo, file=fn))

def big(u):
    return re.sub(r"=s\d+[^/]*$", "", u) + "=s1000"

def dl(rec):
    if not rec["photo"]:
        return None
    p = os.path.join(PH, rec["file"])
    if os.path.exists(p) and os.path.getsize(p) > 1000:
        return None
    err = ""
    for url in (big(rec["photo"]), rec["photo"]):
        try:
            data = urllib.request.urlopen(url, timeout=30).read()
            if len(data) > 500:
                open(p, "wb").write(data)
                return None
        except Exception as e:
            err = str(e)
    return (rec["full"], err)

with cf.ThreadPoolExecutor(12) as ex:
    fails = [f for f in ex.map(dl, recs) if f]

# HubSpot import file
with open(os.path.join(OUT, "K26_hubspot_import.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["First Name", "Last Name", "Phone Number", "Email", "Company Name", "Job Title", "K26 Photo URL"])
    for r in recs:
        w.writerow([r["first"] or r["full"], r["last"], r["phone"], r["email"], r["company"], r["title"],
                    big(r["photo"]) if r["photo"] else ""])
# index for photo uploads
with open(os.path.join(OUT, "K26_index.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["idx", "full", "phone", "file"])
    for r in recs:
        w.writerow([r["idx"], r["full"], r["phone"], r["file"]])
n = sum(1 for r in recs if r["file"] and os.path.exists(os.path.join(PH, r["file"])))
print("records", len(recs), "photos_on_disk", n, "fails", len(fails))
for x in fails[:10]:
    print("FAIL", x)
