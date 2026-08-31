function Login() {
    return (
        <div className="flex h-screen justify-center items-center">

            <div className="w-96 bg-white p-8 rounded-xl shadow">

                <h1 className="text-3xl font-bold mb-5">
                    Login
                </h1>

                <input
                    className="border w-full p-3 mb-4"
                    placeholder="Email"
                />

                <input
                    type="password"
                    className="border w-full p-3 mb-4"
                    placeholder="Password"
                />

                <button className="w-full bg-black text-white p-3 rounded">
                    Login
                </button>

            </div>
        </div>
    );
}

export default Login;