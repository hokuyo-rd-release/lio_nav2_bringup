# lio_nav2_bringup

LIOベース2D Navigation実行環境

# インストール

```
cd ros2_ws/src
git clone --recurse -b ROS2 https://github.com/kiyoshiiriemon/simple_fastlio_localization/
git clone --recurse https://github.com/hokuyo-furo-org/lio_nav2_bringup/
cd ../
sudo rosdep init # まだrosdepを一度も実行していなければ
rosdep update
rosdep install --from-paths src/lio_nav2_bringup --ignore-src -r -y
rosdep install --from-paths src/simple_fastlio_localization --ignore-src -r -y
colcon build --symlink-install
```

# 豊中データでの動作方法
## 自己位置推定の起動

```
export MAP_DIR=<地図のディレクトリ>

ros2 launch simple_fastlio_localization localization.py \
map_file:=$MAP_DIR/toyonaka.pcd \
initial_pose:="0 0 0 0 0 0.9839859 -0.1782461" \
odom_topic:=/hokuyo_lio/lidar_odom \
cloud_odom_topic:=/hokuyo_lio/aligned_scan_points \
publish_2d_pose:=true \
frames_accumulate:=4 \
enable_lio_only_update:=false \
rviz:=true \
rviz_config:=$(ros2 pkg prefix lio_nav2_bringup)/share/lio_nav2_bringup/rviz/loc.rviz \
visualize_registration_result:=true \
enable_sound:=true
```
- パラメータ
   - map_file: 3D地図PCDファイル
   - initial_pose: 初期位置姿勢(x,y,z,qx,qy,qz,qw)
   - odom_topic: LIOオドメトリのトピック
   - cloud_odom_topic: LIO座標系での点群トピック
   - publish_2d_pose: 2Dに投影した位置姿勢を配信（必要）
   - frames_accumulate: レジストレーションに使う点群を何フレーム集積するか
   - enable_lio_only_update: レジストレーションのタイミングだけではなく，LIOのタイミングで更新した自己位置を配信する
   - rviz: rviz2を起動する
   - visualize_registration_result: 地図に対するレジストレーションの成功失敗の可視化
   - enable_sound: 地図に対するレジストレーションの成功失敗の効果音で通知
 
## Navigation2の起動
```
export $MAP_DIR=<地図のディレクトリ>

ros2 launch lio_nav2_bringup navigation_launch.py map:=$MAP_DIR/toyonaka.yaml
```
- パラメータ
  - map: 2D地図設定ファイル(yaml)
  - parmas_file: nav2設定ファイル (デフォルトは config/nav2_params.yaml)
- 目標位置の指定はrvizの「2D Goal Pose」から与えることができる
- 初期位置の指定はsimple_fastlio_localizationの起動パラメータで与える(3次元)

# ソフトウェアの説明
## 概要
- Nav2からamclを削除
- simple_fastlio_localizationを利用し、3次元地図に対する自己位置推定→2次元に投影
- オドメトリをLIOに置換え (豊中データのLIOデータで動作するよう)

## 座標系の設定について
- 2D地図と3D地図の原点は一致することが前提
- /map -> /lio_odomは3次元座標での位置姿勢
- /map -> /odomは投影した2次元平面位置姿勢（Nav2用）
- /hokuyo3d /scanトピックもこの座標になる
- /base_linkは/hokuyo3d (Lidar)と一致
   - LIOからの3D位置姿勢を使う場合は座標変換に注意が必要
- オドメトリ（/odom -> /base_link）はLIOを使用する想定。車輪オドメトリを使用する場合はtf構成の修正が必要

# 変更履歴
- 2025/7/8 レジストレーションの状況の可視化・可聴化オプションの説明を追加
- 2025/6/15 初版
