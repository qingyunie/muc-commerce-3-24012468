# 第9天学生项目：机器学习零基础数据准备

## 运行方法

```bash
python -m pip install -r requirements.txt
python validate_day09_environment.py
jupyter lab
```

打开`notebooks/day09_ml_preparation_student.ipynb`。Notebook已经提供完整处理骨架，你只需完成少量关键填空、运行检查点并撰写解释。

## 学生信息

- 姓名：王一维
- 学号：24012468
- 班级：3班

## 用自己的话回答

- 什么是特征，什么是标签：特征是模型的"输入线索"，如用户的Tenure、Complain等属性；标签是我们要预测的"答案"，即Churn是否流失
- 为什么要保留测试集：模型上线后面对的是未来的、未知的新用户。测试集上的性能才是模型真实泛化能力的反映。
- 为什么83%准确率仍可能没有用：190 个真实流失用户一个都没找到，模型虽然"准确率高"，但对核心问题（识别谁会流失）毫无贡献（因为约 83% 的用户本来就不流失）
