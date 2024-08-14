package str;
public class t1{
    static {
            System.loadLibrary("hello2"); // Load native library at runtime
        }
    private native String string2CStr(String s);
    public void hello(){
        System.out.println("Hello!");
    }
    public static void main(String[] args){
        String a = string2CStr("456");
        System.out.println(a);
    }
}