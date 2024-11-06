import os
import re
import requests
import pandas as pd
import time

from bs4 import BeautifulSoup


def get_url_mapping():
    # with open('racknerd-category.html', 'r', encoding='utf-8') as fr:
    #     html_doc = fr.read()
    # soup = BeautifulSoup(html_doc, 'html.parser')

    url = "https://my.racknerd.com/index.php?rp=/store/kvm-vps"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Failed to retrieve data: {response.status_code}"
    soup = BeautifulSoup(response.content, 'html.parser')
    categories = soup.find('div', menuitemname='Categories')
    print(type(categories))
    print(categories.prettify())
    print('*'*120)
    items = categories.find_all('a')
    cat_url_mapping = {}
    for item in items:
        print('*'*120)
        print(item.prettify())
        attrs = item.attrs
        url = host + attrs['href']
        cat = attrs['menuitemname']
        if cat not in cat_url_mapping:
            cat_url_mapping[cat] = url
    print(cat_url_mapping)
    print(len(cat_url_mapping))
    return cat_url_mapping


def parse_product_infos(cat, url):
    print("\n")
    print('*'*120)
    print('*'*120)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Failed to retrieve data: {response.status_code}"
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', class_='product')
    product_list = []
    for product in products:
        # print('*'*120)
        # print(product.attrs)
        # print(product.header.text)
        # print(product.prettify())
        p_name = product.header.text.strip()
        pid_info = product.attrs['id']
        pid = re.search(r'\d+', pid_info)
        pid = pid.group() if pid else None

        # description = product.find('p').get_text(strip=True)
        description = product.find('p').text.strip()
        # print(description)
        # cpu = re.search(r'(\d+\s*(?:vCPU))', description, re.I)
        cpu = re.search(r'(\d+\s*x?\s*vCPU)', description, re.I)
        cpu = cpu.group(1) if cpu else None

        # disk = re.search(r'(\d+ GB SSD).*', description)
        # disk = re.search(r'(\d+\s*(?:GB|TB|MB))(?=\s+SSD|\s+NVMe)', description, re.I)
        # - (\d+\s*(?:GB|TB|MB))：匹配数字 + 可选空格 + 单位（GB、TB 或 MB），并捕获这一部分
        # - (?=\s+(?:\w+\s+)*\b(?:SSD|NVMe)\b)：正向前瞻，确保后面跟着零个或多个单词，最后是 SSD 或 NVMe
        disk = re.search(r'(\d+\s*(?:GB|TB|MB))(?=\s+(?:\w+\s+)*\b(?:SSD|NVMe)\b)', description, re.I)

        disk = disk.group(1) if disk else None

        # ram = re.search(r'(\d+[MB|GB])', description)
        # ram = re.search(r'(\d+\s*(?:MB|GB))(?=\s+RAM |\s+DDR[\d] RAM)', description, re.I)
        ram = re.search(r'(\d+(?:\.\d+)?\s*(?:MB|GB))(?=\s+RAM|\s+DDR\d RAM)', description, re.I)
        ram = ram.group(1) if ram else None

        # bandwidth = re.search(r'(\d+[GB|TB Month]).*', description)
        # bandwidth = re.search(r'(\d+\s*(?:GB|TB|MB) Monthly [\w\s]+)', description)
        # 匹配数字、可选空格和单位，但后面需跟 "Monthly" 或 "Bandwidth"
        bandwidth = re.search(r'(\d+\s*(?:GB|TB|MB))\s+(?=\w+\s+Bandwidth|Monthly)', description, re.I)
        bandwidth = bandwidth.group(1) if bandwidth else None

        # bps = re.search(r'(\d+Gbps)', description)
        bps = re.search(r'(\d+\s*(?:Gbps|Mbps))(?=\s+Public Network Port|\s+Bandwidth)', description, re.I)
        bps = bps.group(1) if bps else None
        # print(cpu, disk, ram, bandwidth, bps)

        infos = product.footer.div.get_text(strip=True)
        # print('DDDDDDDDDDDDDDDDDDDDDDDDDD')
        # print(infos)
        match = re.search(r'\$([\d.]+)\s+USD\s*(Monthly|Annually)', infos, re.I)
        price = match.group(1) if match else None
        period = match.group(2) if match else None
        output = {
            'cat': cat,
            'pid': pid,
            'p_name': p_name,
            'cpu': cpu,
            'disk': disk,
            'ram': ram,
            'bandwidth': bandwidth,
            'bps': bps,
            'price': price,
            'period': period,
            'aff': f"https://my.racknerd.com/aff.php?aff=12682&pid={pid}"
        }
        product_list.append(output)
    df = pd.DataFrame(product_list)
    print(df)
    csv_path = os.path.join(data_dir, f"{cat.replace('/', ' or ')}-products.csv")
    df.to_csv(csv_path, index=False)
    return df


if __name__ == "__main__":
    data_dir = "./data"
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    host = "https://my.racknerd.com"
    cat_url_mapping = get_url_mapping()
    all_dfs = []
    for cat, url in cat_url_mapping.items():
        # if '11.11 Specials' not in cat:
        #     continue
        df = parse_product_infos(cat, url)
        all_dfs.append(df)
        print(f"[Done] {cat}: {url}")
        time.sleep(8)
    final_df = pd.concat(all_dfs, ignore_index=True)
    print(final_df)
    final_df.to_csv(os.path.join(data_dir, "all-products.csv"), index=False)



