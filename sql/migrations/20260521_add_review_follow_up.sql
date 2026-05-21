-- Add follow-up review support.
USE ecommerce_db;

ALTER TABLE t_review
    ADD COLUMN follow_up_comment TEXT DEFAULT NULL COMMENT '追评内容' AFTER admin_reply,
    ADD COLUMN follow_up_images TEXT DEFAULT NULL COMMENT '追评图片JSON数组' AFTER follow_up_comment,
    ADD COLUMN follow_up_time DATETIME DEFAULT NULL COMMENT '追评时间' AFTER follow_up_images;
