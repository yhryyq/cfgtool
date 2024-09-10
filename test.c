#include <jni.h>
#include <stdio.h>

JNIEXPORT jobject JNICALL Java_com_string2CStr(JNIEnv env, jstring jstr) {
    char *rtn = NULL;
    jclass classtring = env.FindClass("java/lang/String");
    jstring strencode = env.NewStringUTF("GB2312");
    jmethodID mid = env.GetMethodID(classtring, "getBytes", "(Ljava/lang/String;)[B");
    jbyteArray barr = (jbyteArray) env.CallObjectMethod(jstr, mid, strencode);
    jsize alen = env.GetArrayLength(barr);
    jbyte *ba = env.GetByteArrayElements(barr, JNI_FALSE);
 
    env.ReleaseByteArrayElements(barr, ba, 0);
    return rtn;
}