using System;

namespace checkin.core.message
{
    public class ResultTuple<T,G>
    {
        public bool Status { get; set; }

        public T Left { get; set; }

        public G Right { get; set; }

        public ResultTuple (bool status, T left, G right)
        {
            Status = status;
            Left = left;
            Right = right;
        }
    }

    public class Failure<T,G> : ResultTuple<T,G>
    {
        public Failure (T result) : base (false, result, default(G))
        {
        }

        public T Result {
            get { return Left; }
            set { Left = value; }
        }
    }

    public class Success<T,G> : ResultTuple<T,G>
    {
        public Success (G result) : base (true, default(T), result)
        {
        }

        public G Result {
            get { return Right; }
            set { Right = value; }
        }
    }
}

