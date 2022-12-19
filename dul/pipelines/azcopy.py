from enum import Enum

from . import curl
from .cli_helpers import Flag, Once, Positional, Repeat, Schema, pipe


class Loglevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    NONE = "NONE"


class OutputLevel(Enum):
    DEFAULT = "default"
    ESSENTIAL = "essential"
    QUIET = "quiet"


class BlobType(Enum):
    DETECT = "Detect"
    BLOCK_BLOB = "BlockBlob"
    PAGE_BLOB = "PageBlob"
    APPEND_BLOB = "AppendBlob"


class BlobTier(Enum):
    HOT = "hot"
    COOL = "cool"
    ARCHIVE = "archive"


class CheckMD5Type(Enum):
    NO_CHECK = "NoCheck"
    LOG_ONLY = "LogOnly"
    FAIL_IF_DIFFERENT = "FailIfDifferent"
    FAIL_IF_DIFFERENT_OR_MISSING = "FailIfDifferentOrMissing"


class SnapshotRemovalType(Enum):
    INCLUDE = "include"
    ONLY = "only"


class OverwriteType(Enum):
    TRUE = "true"
    FALSE = "false"
    IF_SOURCE_NEWER = "ifSourceNewer"


def flag(name): return lambda: [name]
def once(name): return lambda value: [name, value]
def repeat_list(name): return once(name)
def repeat_dict(name): return lambda k, v: [name, f"{k}={v}"]


class cli(pipe):
    def __init__(
        self, cap_mbps: float = None, log_level: Loglevel = None,
        output_level: OutputLevel = None, output_type: OutputLevel = None,
        trusted_microsoft_suffixes: str = None, version: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "cap_mbps": Once(once("--cap-mbps")),
                "log_level": Once(once("--log-level")),
                "output_level": Once(once("--output-level")),
                "output_type": Once(once("--output-type")),
                "trusted_microsoft_suffixes": Once(once("--trusted-microsoft-suffixes")),
                "version": Flag(flag("--version")),
                "aad_endpoint": Once(once("--aad-endpoint")),
                "application_id": Once(once("--application-id")),
                "certificate_path": Once(once("--certificate-path")),
                "identity": Flag(flag("--identity")),
                "identity_client_id": Once(once("--identity-client-id")),
                "identity_object_id": Once(once("--identity-object-id")),
                "identity_resource_id": Once(once("--identity-resource-id")),
                "service_principal": Once(once("--service-principal")),
                "tenant_id": Once(once("--tenant-id")),
                "as_subdir": Flag(flag("--as-subdir")),
                "backup": Flag(flag("--backup")),
                "blob_tags": Repeat(repeat_list("--blob-tags")),
                "blob_type": Once(once("--blob-type")),
                "block_blob_tier": Once(once("--block-blob-tier")),
                "block_size_mb": Once(once("--block-size-mb")),
                "cache_control": Once(once("--cache-control")),
                "check_length": Flag(flag("--check-length")),
                "check_md5": Once(once("--check-md5")),
                "content_disposition": Once(once("--content-disposition")),
                "content_encoding": Once(once("--content-encoding")),
                "content_language": Once(once("--content-language")),
                "content_type": Once(once("--content-type")),
                "cpk_by_name": Once(once("--cpk-by-name")),
                "cpk_by_value": Once(once("--cpk-by-value")),
                "decompress": Flag(flag("--decompress")),
                "disable_auto_decoding": Flag(flag("--disable-auto-decoding")),
                "dry_run": Flag(flag("--dry-run")),
                "exclude_attributes": Repeat(repeat_list("--exclude-attributes")),
                "exclude_blob_type": Repeat(repeat_list("--exclude-blob-type")),
                "exclude_path": Repeat(repeat_list("--exclude-path")),
                "exclude_pattern": Repeat(repeat_list("--exclude-pattern")),
                "exclude_regex": Repeat(repeat_list("--exclude-regex")),
                "follow_symlinks": Flag(flag("--follow-symlinks")),
                "force_if_read_only": Flag(flag("--force-if-read-only")),
                "from_to": Once(once("--from-to")),
                "include_after": Once(once("--include-after")),
                "include_attributes": Repeat(repeat_list("--include-attributes")),
                "include_before": Once(once("--include-before")),
                "include_directory_stub": Flag(flag("--include-directory-stub")),
                "include_path": Repeat(repeat_list("--include-path")),
                "include_pattern": Repeat(repeat_list("--include-pattern")),
                "include_regex": Repeat(repeat_list("--include-regex")),
                "list_of_versions": Once(once("--list-of-versions")),
                "metadata": Repeat(repeat_dict("--metadata")),
                "no_guess_mime_type": Flag(flag("--no-guess-mime-type")),
                "overwrite": Once(once("--overwrite")),
                "page_blob_tier": Once(once("--page-blob-tier")),
                "preserve_last_modified_time": Flag(flag("--preserve-last-modified-time")),
                "preserve_owner": Flag(flag("--preserve-owner")),
                "preserve_permissions": Flag(flag("--preserve-permissions")),
                "preserve_posix_properties": Flag(flag("--preserve-posix-properties")),
                "preserve_smb_info": Flag(flag("--preserve-smb-info")),
                "put_md5": Flag(flag("--put-md5")),
                "recursive": Flag(flag("--recursive")),
                "s2s_detect_source_changed": Flag(flag("--s2s-detect-source-changed")),
                "s2s_handle_invalid_metadata": Flag(flag("--s2s-handle-invalid-metadata")),
                "s2s_preserve_access_tier": Flag(flag("--s2s-preserve-access-tier")),
                "s2s_preserve_blob_tags": Flag(flag("--s2s-preserve-blob-tags")),
                "s2s_preserve_properties": Flag(flag("--s2s-preserve-properties")),
                "delete_destination": Once(lambda v: f"{v}".lowercase()),
                "mirror_mode": Flag(flag("--mirror-mode")),
                "delete_snapshots": Once(once("--delete-snapshots")),
                "list_of_files": Once(lambda v: ["--list-of-files", "\n".join(v)]),
                "permanent_delete": Once(once("--permanent-delete"))
            }
        )
        self.cli = ["azcopy"] + extra_args + \
            self.schema.process(parameters)

    def login(
        self, aad_endpoint: str = None, application_id: str = None, certificate_path: str = None,
        identity: bool = None, identity_client_id: str = None, identity_object_id: str = None,
        identity_resource_id: str = None, service_principal: bool = None, tenant_id: str = None,
        extra_args: list = []
    ) -> pipe:
        self.cli += ["login"] + extra_args + self.schema.process(locals())
        return self

    def copy(
        self, source: str, destination: str, as_subdir: bool = None, backup: bool = None,
        blob_tags: list[str] = None, blob_type: BlobType = None,
        block_blob_tier: BlobTier = None, block_size_mb: float = None,
        cache_control: str = None, check_length: bool = None, check_md5: CheckMD5Type = None,
        content_disposition: str = None, content_encoding: str = None,
        content_language: str = None, content_type: str = None, cpk_by_name: str = None,
        cpk_by_value: str = None, decompress: bool = None, disable_auto_decoding: bool = None,
        dry_run: bool = None, exclude_attributes: list[str] = None,
        exclude_blob_type: list[BlobType] = None, exclude_path: list[str] = None,
        exclude_pattern: list[str] = None, exclude_regex: list[str] = None,
        follow_symlinks: bool = None, force_if_read_only: bool = None, from_to: str = None,
        include_after: str = None, include_attributes: list[str] = None,
        include_before: str = None, include_directory_stub: bool = None,
        include_path: list[str] = None, include_pattern: list[str] = None,
        include_regex: list[str] = None, list_of_versions: str = None, metadata: dict = None,
        no_guess_mime_type: bool = None, overwrite: OverwriteType = None,
        page_blob_tier: BlobTier = None, preserve_last_modified_time: bool = None,
        preserve_owner: bool = None, preserve_permissions: bool = None,
        preserve_posix_properties: bool = None, preserve_smb_info: bool = None,
        put_md5: bool = None, recursive: bool = None, s2s_detect_source_changed: bool = None,
        s2s_handle_invalid_metadata: bool = None, s2s_preserve_access_tier: bool = None,
        s2s_preserve_blob_tags: bool = None, s2s_preserve_properties: bool = None,
        extra_args: list = []
    ) -> pipe:
        self.cli += ["copy"] + extra_args + self.schema.process(locals())
        return self

    def sync(
        self, source: str, destination: str, block_size_mb: float = None,
        check_md5: CheckMD5Type = None, cpk_by_name: str = None, cpk_by_value: str = None,
        delete_destination: bool = None, dry_run: bool = None,
        exclude_attributes: list[str] = None, exclude_path: list[str] = None,
        exclude_pattern: list[str] = None, exclude_regex: list[str] = None, from_to: str = None,
        include_attributes: list[str] = None, include_pattern: list[str] = None,
        include_regex: list[str] = None, mirror_mode: bool = None,
        preserve_permissions: bool = None, preserve_posix_properties: bool = None,
        preserve_smb_info: bool = None, put_md5: bool = None, recursive: bool = None,
        s2s_preserve_access_tier: bool = None, s2s_preserve_blob_tags: bool = None,
        extra_args: list = []
    ) -> pipe:
        self.cli += ["sync"] + extra_args + self.schema.process(locals())
        return self

    def remove(
        self, delete_snapshots: SnapshotRemovalType = None, dry_run: bool = None,
        exclude_path: list[str] = None, exclude_pattern: list[str] = None,
        force_if_read_only: bool = None, from_to: str = None, include_after: str = None,
        include_before: str = None, include_path: list[str] = None,
        include_pattern: list[str] = None, list_of_files: list[str] = None,
        list_of_versions: str = None, permanent_delete: bool = None, recursive: bool = None,
        extra_args: list = []
    ) -> pipe:
        self.cli += ["remove"] + extra_args + self.schema.process(locals())
        return self
