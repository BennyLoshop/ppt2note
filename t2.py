import json
from pathlib import Path
import hashlib
import datetime
import uuid
import api

# ========== 配置 ==========
def uploadNote(output_file = "reconstructed.json",user_id = None,token = "",name=""):
    download_root = Path(
        "storage/emulated/0/Android/data/com.friday.cloudsnote/userNote/30875/note"
    )
    custom_fileId = api.generate_custom_fileid()
    oss_base_url = "http://ezy-sxz.oss-cn-hangzhou.aliyuncs.com/note_v2/res"


    # ========== 工具函数 ==========
    def calc_md5(file_path: Path) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest().upper()


    def get_resource_type(file_path: Path) -> int:
        if file_path.suffix.lower() in [".png"]:
            return 2
        if file_path.suffix.lower() in [".webp"]:
            return 0
        return 1


    # ========== 获取 pageHash 排序 ==========
    file_root = download_root / "731743cada2f462c9476fb73d69231f5"
    page_hash_dirs = [d for d in file_root.iterdir() if d.is_dir()]
    # 按文件夹名称转 int 排序
    sorted_page_hash = sorted(page_hash_dirs, key=lambda x: int(x.name))
    page_index_map = {d.name: idx for idx, d in enumerate(sorted_page_hash)}

    # ========== 遍历文件生成 resourceList ==========
    resource_list = []

    for pageHash in sorted_page_hash:
        for file_path in pageHash.rglob("*"):
            if not file_path.is_file():
                continue

            if get_resource_type(file_path) == 0:
                android_id = (
                    f"/storage/emulated/0/Android/data/com.friday.cloudsnote/"
                    f"userNote/{user_id}/note/{custom_fileId}/{pageHash.name}/res/image/{file_path.name}"
                )
            else:
                android_id = (
                    f"/storage/emulated/0/Android/data/com.friday.cloudsnote/"
                    f"userNote/{user_id}/note/{custom_fileId}/{pageHash.name}/{api.get_uuid_or_res(file_path)}{file_path.name}"
                )

            pageName = f"/storage/emulated/0/Android/data/com.friday.cloudsnote/userNote/{user_id}/note/{custom_fileId}/{pageHash.name}"

            # timestamp 从 pageHash 转换
            try:
                timestamp = datetime.datetime.fromtimestamp(
                    int(pageHash.name) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            today_str = datetime.datetime.now().strftime("%Y%m%d")
            oss_url = f"{oss_base_url}/{user_id}/{today_str}/{custom_fileId}/{pageHash.name}/{api.get_uuid_or_res(file_path)}{file_path.name}"

            # 上传文件
            params = api.parse_oss_url(oss_url)
            final_url = api.upload(
                V=1,
                nonce=params[0],
                filename=params[1],
                sourcePath=file_path,
                user_id=user_id,
                token=token,
            )
            print(final_url)

            resource = {
                "id": android_id,
                "fileId": custom_fileId,
                "pageName": pageName,
                "pageIndex": page_index_map[pageHash.name],  # 根据排序生成 pageIndex
                "md5": calc_md5(file_path),
                "resourceType": get_resource_type(file_path),
                "ossImageUrl": final_url,
                "createTimeStamp": timestamp,
                "updateTimeStamp": timestamp,
                "toBeUploaded": False,
                "wasDeleted": False,
            }

            resource_list.append(resource)

    # ========== 构建 JSON ==========
    output_data = {
        "code": "sxz",
        "userId": user_id,
        "totalCount": len(resource_list),
        "resourceList": resource_list,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"✅ JSON 已生成: {output_file}")

    api.addOrUpdateResource(resource_list, token)

    new_url = f"http://ezy-sxz.oss-cn-hangzhou.aliyuncs.com/note_v2/res/{user_id}/{today_str}/{custom_fileId}/"
    api.addOrUpdateNote(custom_fileId, name, "0", 12, new_url, token)
