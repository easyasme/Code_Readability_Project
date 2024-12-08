import os
from typing import List, Optional
from fastapi import APIRouter, Cookie, File, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import config
from utils import password_utils, user_utils, files_utils, get_data_utils

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 下载文件的路由
@router.get("/download")
async def download_file(
    file_id: Optional[str] = None,  # 添加查询参数
    access_token: Optional[str] = Cookie(None),  # 读取 Cookie
    unlock_folder: Optional[str] = Cookie(None),  # 解密文件夹
):
    # 判断是否登录
    username = await user_utils.isLogin_getUser(access_token)
    if not username:
        return {"error": "未登录"}
    lock_folder_id = await files_utils.get_parent_folder_id_is_locked(username, file_id)
    if lock_folder_id:  # 文件的父类文件夹被加密
        if not unlock_folder:
            return {"error": "文件所属的文件夹被加密，请先解密再使用"}
        if not await password_utils.verify_password(unlock_folder, lock_folder_id):
            return {"error": "文件所属的文件夹未解密，请先解密再使用"}
    file_dict = await files_utils.verify_and_return_files_info(username, file_id)
    if not file_dict:
        return {"error": "文件不存在"}
    file_path = file_dict.get("file_path")
    file_name = file_dict.get("file_name")
    # 使用原始文件路径拼接文件路径
    if not os.path.exists(file_path):
        return {"error": "因无法预料的原因，文件消失了"}

    return FileResponse(
        path=file_path,
        filename=file_name,
    )


@router.post("/upfile")  # 上传文件
async def upload_file(
    folder_id: Optional[str] = None,  # 添加查询参数
    files: List[UploadFile] = File(...),
    access_token: Optional[str] = Cookie(None),  # 读取 Cookie
    unlock_folder: Optional[str] = Cookie(None),  # 解密文件夹
):
    username = await user_utils.isLogin_getUser(access_token)
    if not username:
        return {"error": "未登录"}
    if folder_id and files:  # 上传文件
        if await files_utils.is_folder_encrypted(username, folder_id):  # 文件夹被加密
            if not unlock_folder:
                return {"error": "文件夹被加密，请先解密再使用"}
            if not await password_utils.verify_password(unlock_folder, folder_id):
                return {"error": "该文件夹未解密，请先解密再使用"}

        for file in files:  # 遍历上传的文件
            contents = await file.read()  # 读取文件内容
            file_name = file.filename  # 文件名
            file_size_bytes = len(contents)  # 文件大小（字节）
            file_size_kb = round(
                file_size_bytes / 1024, 2
            )  # 文件大小（KB），保留两位小数
            # 最大上传文件大小限制
            max_upload_file_size_kb = await files_utils.get_max_upload_file_size_kb(
                username
            )
            if file_size_kb > max_upload_file_size_kb:
                return {
                    "error": f"文件大小超过限制，{await get_data_utils.convert_kb_to_human_readable(max_upload_file_size_kb)}"
                }
            if await files_utils.verify_capacity_exceeded(username, file_size_kb):
                return {"error": "容量不足，请清理文件后再上传"}
            # 保存文件，获取文件id，并更新用户已使用容量
            file_id = await files_utils.save_file_get_file_id(
                username, file_name, file_size_kb, folder_id
            )
            user_all_file_path = os.path.join(
                config.user_files_path, username
            )  # 用户的文件夹
            file_path = os.path.join(user_all_file_path, file_id)

            with open(file_path, "wb") as f:
                f.write(contents)  # 写入文件内容
        return (
            RedirectResponse(url="/index", status_code=303)
            if folder_id == "/"
            else RedirectResponse(url=f"/index/{folder_id}", status_code=303)
        )

    return {"error": "上传失败"}
